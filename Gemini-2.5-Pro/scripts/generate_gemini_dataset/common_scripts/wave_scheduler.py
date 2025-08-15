from __future__ import annotations
import asyncio
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Deque, Dict, List, Optional
from logging_utils import Logger, LoggingStats

try:
    from google import genai  # optional; replace with any client if needed
except Exception:
    genai = None  # type: ignore

@dataclass
class KeyState:
    email: str
    project: str
    api_key: str
    client: Any | None = None
    used_today: int = 0
    quarantined_until: float = 0.0  # if 429 / transient throttle

    @property
    def label(self) -> str:
        return f"{self.email}:{self.project}"

@dataclass
class SchedulerConfig:
    rpm_per_key: int                 # requests per minute per key
    rpd_per_key: int                 # requests per day per key
    max_concurrent: int              # number of keys per batch (1 task per key)
    align_to_minute: bool = True     # align the first bucket to the next :00
    max_retries_per_item: int = 2
    minute_seconds: int = 60         # size of the minute bucket (normally 60)

class WaveScheduler:
    """
    Batch-by-keys scheduler:
      - Pick up to MAX_CONCURRENT *keys* per batch.
      - Launch exactly 1 task per selected key.
      - Wait for the whole batch to finish.
      - If time remains in the current minute bucket, pick the NEXT set of keys (round-robin),
        still at most RPM_PER_KEY requests per key per minute.
      - When the minute rolls over, per-key minute counters reset.
    Also enforces per-key RPD and quarantines keys for the remainder of the minute on 429.
    """
    def __init__(
        self,
        keys: List[KeyState],
        cfg: SchedulerConfig,
        on_client_factory: Optional[Callable[[str], Any]] = None,
        on_log: Optional[Callable[[str], None]] = None,
    ):
        if cfg.rpm_per_key <= 0 or cfg.rpd_per_key <= 0 or cfg.max_concurrent <= 0:
            raise ValueError("rpm_per_key, rpd_per_key, and max_concurrent must be positive.")
        self.keys = keys
        self.cfg = cfg
        self.log = on_log or (lambda msg: print(msg, flush=True))
        self._client_factory = on_client_factory or self._default_client_factory
        self._sem = asyncio.Semaphore(cfg.max_concurrent)

        # Build clients
        for k in self.keys:
            k.client = self._client_factory(k.api_key)

        # Round-robin pointer across all keys
        self._rr_index = 0

        # Per-minute usage tracking
        self._minute_used: Dict[int, int] = defaultdict(int)  # index -> count in current minute
        self._bucket_start: Optional[float] = None

    def _default_client_factory(self, api_key: str):
        if genai is None:
            return {"api_key": api_key}  # dummy client for testing
        return genai.Client(api_key=api_key)

    def _align_to_minute(self):
        if not self.cfg.align_to_minute:
            self._bucket_start = time.time()
            return
        now = time.time()
        delay = (60.0 - (now % 60.0)) % 60.0
        if delay > 0.01:
            self.log(f"[batch] aligning to next minute in {delay:.2f}s ...")
            time.sleep(delay)
        self._bucket_start = time.time()

    def _bucket_time_left(self) -> float:
        assert self._bucket_start is not None
        return max(0.0, self.cfg.minute_seconds - (time.time() - self._bucket_start))

    def _roll_minute_if_needed(self):
        assert self._bucket_start is not None
        if time.time() - self._bucket_start >= self.cfg.minute_seconds:
            # new minute bucket
            self._bucket_start += self.cfg.minute_seconds
            # reset per-minute counts
            self._minute_used.clear()
            # also clear any minute-only quarantines
            for k in self.keys:
                if k.quarantined_until <= self._bucket_start:
                    k.quarantined_until = 0.0
            self.log("[batch] minute window rolled over; per-key minute counters reset.")

    def _keys_available(self) -> List[int]:
        """Return indices of keys that can be used *now* (minute + day + quarantine)."""
        now = time.time()
        idxs: List[int] = []
        for i, k in enumerate(self.keys):
            if k.used_today >= self.cfg.rpd_per_key:
                continue
            if now < k.quarantined_until:
                continue
            # Per-minute allowance: at most rpm_per_key times per minute.
            if self._minute_used[i] >= self.cfg.rpm_per_key:
                continue
            idxs.append(i)
        return idxs

    def _pick_next_batch(self, available_idxs: List[int], batch_size: int) -> List[int]:
        """Pick up to batch_size keys using global round-robin order (over available)."""
        if not available_idxs:
            return []
        chosen: List[int] = []
        n_all = len(self.keys)
        j = 0
        # Iterate up to n_all positions, collecting available ones in order
        while len(chosen) < batch_size and j < n_all:
            idx = (self._rr_index + j) % n_all
            if idx in available_idxs:
                chosen.append(idx)
            j += 1
        # Advance rr pointer past the last *global* position we looked at
        self._rr_index = (self._rr_index + j) % n_all
        return chosen

    async def run(
        self,
        work_items: List[Any],
        worker: Callable[[Any, Any], Awaitable[None]],  # worker(client, item)
        logger: Logger,
        logging_stats: LoggingStats,
    ):
        queue: Deque[Any] = deque(work_items)
        retry_counts: Dict[int, int] = defaultdict(int)

        # Start in-sync with a minute bucket
        if self._bucket_start is None:
            self._align_to_minute()

        batch_num = 0
        while queue:
            # minute rollover if needed
            self._roll_minute_if_needed()

            available = self._keys_available()
            if not available:
                # No key can be used right now. Sleep until bucket end (or a small slice).
                sleep_for = max(0.01, self._bucket_time_left())
                self.log(f"[batch] no keys available; sleeping {sleep_for:.2f}s until next minute window.")
                await asyncio.sleep(sleep_for)
                continue

            # Choose up to MAX_CONCURRENT keys (1 task per key)
            batch_size = min(self.cfg.max_concurrent, len(available), len(queue))
            selected = self._pick_next_batch(available, batch_size)
            if not selected:
                await asyncio.sleep(min(0.5, self._bucket_time_left()))
                continue

            batch_num += 1
            self.log(f"[batch #{batch_num}] launching {len(selected)} tasks; queue={len(queue)}")

            tasks: List[asyncio.Task] = []
            # Launch one item per selected key
            for idx in selected:
                if not queue:
                    break
                item = queue.popleft()
                key = self.keys[idx]

                async def _run_one(kidx: int, it: Any, kstate: KeyState):
                    async with self._sem:
                        try:                                                    
                            await worker(kstate.client, it)
                        except Exception as e:
                            logging_stats.num_failed += 1
                            logger.log_failure(
                                entry=it,
                                error_msg=f"Email = {kstate.email}, Project = {kstate.project}, Worker error: {e}"
                            )
                            # self.log(f"[{kstate.label}] task failed: {e}")
                            # Quarantine key until end of minute on rate-ish errors
                            msg = str(e).lower()
                            if "resourceexhausted" in msg or "429" in msg or "rate" in msg:
                                kstate.quarantined_until = max(kstate.quarantined_until, (self._bucket_start or time.time()) + self.cfg.minute_seconds)
                            # Requeue with bounded retries
                            iid = id(it)
                            retry_counts[iid] += 1
                            if retry_counts[iid] <= self.cfg.max_retries_per_item:
                                queue.append(it)
                            #     self.log(f"[{kstate.label}] task failed (retry {retry_counts[iid]}/{self.cfg.max_retries_per_item}): {e}")
                            # else:
                            #     self.log(f"[{kstate.label}] task failed permanently: {e}")
                        else:
                            # Success -> update counters
                            logging_stats.num_success += 1
                            self._minute_used[kidx] += 1
                            kstate.used_today += 1
                        finally:
                            logging_stats.num_processed += 1
                            if logging_stats.log_interval > 0 and logging_stats.num_processed % logging_stats.log_interval == 0:
                                logger.log_success(
                                    f"Processed {logging_stats.num_processed} items so far, "
                                    f"{logging_stats.num_success} success so far, "
                                    f"{logging_stats.num_failed} failed so far.",
                                    meta={
                                        "processed": logging_stats.num_processed,
                                        "success": logging_stats.num_success,
                                        "failed": logging_stats.num_failed
                                    }
                                )
                                print(f"{logger._current_melbourne_iso()}: Processed {logging_stats.num_processed} items so far, "
                                      f"{logging_stats.num_success} success so far, "
                                      f"{logging_stats.num_failed} failed so far.")
                                                           
                tasks.append(asyncio.create_task(_run_one(idx, item, key)))

            # Wait for the whole batch to finish before picking next set
            if tasks:
                await asyncio.gather(*tasks)

            # If time left in minute and queue still non-empty, loop immediately to pick next batch

        self.log("[batch] Done.")
