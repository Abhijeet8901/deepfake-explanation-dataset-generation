import asyncio
import json
from pathlib import Path
from PIL import Image
from api_call import get_explanation_async  # unchanged API function
from logging_utils import Logger

class AsyncRateLimiter:
    def __init__(self, max_calls: int, period: float):
        self._sem = asyncio.Semaphore(max_calls)
        self._max = max_calls
        self._period = period
        asyncio.create_task(self._reset_loop())

    async def _reset_loop(self):
        while True:
            await asyncio.sleep(self._period)
            for _ in range(self._max):
                self._sem.release()

    async def __aenter__(self):
        await self._sem.acquire()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

async def process_entry(entry: dict, limiter: AsyncRateLimiter, prompt_template: str, logger: Logger) -> str:
    out = Path(entry["output_explanation_path"]) / entry["output_explanation_name"]
    if out.exists():
        return f"Skipped: {out.name}"

    out.parent.mkdir(parents=True, exist_ok=True)
    
    try: 
        # Load images
        gen_img = Image.open(entry["generated_image_path"]).convert("RGB")
        real_img = Image.open(entry["real_image_path"]).convert("RGB")

        # Load the specific effect
        effects = json.loads(Path(entry["edit_suggestion_path"])
                        .read_text(encoding="utf-8"))["Effects"]
        effect = effects[entry["image_index"]]
        if(int(prompt_template.split("_")[-1])>=4):
            effect = {
                "Explanation": effect["Explanation"]
            }  

    except Exception as e:
        logger.log_failure(entry, f"File load error: {e}")
        return None        

    try:
        # Rate-limited API call
        async with limiter:
            explanation = await get_explanation_async(gen_img, real_img, effect, prompt_name = prompt_template)
    except Exception as e:
        logger.log_failure(entry, f"API/extraction error: {e}")
        return None
    
    try: 
        # Save result
        out.write_text(json.dumps(explanation, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        logger.log_failure(entry, f"Save error: {e}")
        return None
    
    return f"Saved: {out.name}"

async def run_processing(mappings: list, logger: Logger, prompt_template, rpm = 15, max_concurrent = 150, success_log_interval: int = 1000):
    limiter = AsyncRateLimiter(rpm, period = 70)
    sem = asyncio.Semaphore(max_concurrent)
    num_images_processed = 0
    num_images_success = 0
    num_images_failed = 0

    async def sem_task(entry):
        nonlocal num_images_processed, num_images_success, num_images_failed
        async with sem:
            result = await process_entry(entry, limiter, prompt_template, logger)
            num_images_processed += 1
            if(result is None):
                num_images_failed += 1
            else:
                num_images_success += 1
                                
            if success_log_interval > 0 and num_images_processed % success_log_interval == 0:
                logger.log_success(
                        f"Processed {num_images_processed} images so far, {num_images_success} success so far, {num_images_failed} failed so far.",
                        meta={
                            "processed": num_images_processed,
                            "success": num_images_success,
                            "failed": num_images_failed
                            }
                )
                # Also print to console
                print(f"{logger._current_melbourne_iso()}: Processed {num_images_processed} images so far, {num_images_success} success so far, {num_images_failed} failed so far.")
            
            return result


    tasks = [asyncio.create_task(sem_task(entry)) for entry in mappings]
    for fut in asyncio.as_completed(tasks):
        res = await fut
        # if res:
        #     print(res)
