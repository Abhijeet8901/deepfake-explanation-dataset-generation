import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

class Logger:
    def __init__(
        self,
        error_logs_dir: Path = Path("Runtime Logs/Error Logs"),
        success_logs_dir: Path = Path("Runtime Logs/Successful Logs")
    ):
        self.error_logs_dir = error_logs_dir
        self.success_logs_dir = success_logs_dir
        self.error_log_file = self._get_next_run_file(error_logs_dir, "error_logs")
        self.success_log_file = self._get_next_run_file(success_logs_dir, "success_logs")

    def _get_next_run_file(self, directory: Path, prefix: str) -> Path:
        directory.mkdir(parents=True, exist_ok=True)
        existing = sorted(str(p.stem) for p in directory.glob(f"{prefix}_run_*.jsonl"))
        nums = [int(name.replace(f"{prefix}_run_", "")) for name in existing if name.replace(f"{prefix}_run_", "").isdigit()]
        next_num = max(nums, default=0) + 1
        return directory / f"{prefix}_run_{next_num}.jsonl"

    def _current_melbourne_iso(self) -> str:
        tz = ZoneInfo("Australia/Melbourne")
        return datetime.now(tz).isoformat()

    def log_failure(self, entry: dict, error_msg: str):
        record = {
            "timestamp_melbourne": self._current_melbourne_iso(),
            "entry": {
                "generation_model": entry["generation_model"],
                "edit_suggestion_model": entry["edit_suggestion_model"],
                "dataset": entry["dataset"],
                "image_name": entry["image_name"],
                "image_index": entry["image_index"],
            },
            "error": error_msg
        }
        with self.error_log_file.open("a", encoding="utf-8") as fw:
            fw.write(json.dumps(record, ensure_ascii=False) + "\n")

    def log_success(self, message: str, meta: dict = None):
        record = {
            "timestamp_melbourne": self._current_melbourne_iso(),
            "message": message,
        }
        if meta:
            record["meta"] = meta

        # Write to file
        with self.success_log_file.open("a", encoding="utf-8") as fw:
            fw.write(json.dumps(record, ensure_ascii=False) + "\n")
