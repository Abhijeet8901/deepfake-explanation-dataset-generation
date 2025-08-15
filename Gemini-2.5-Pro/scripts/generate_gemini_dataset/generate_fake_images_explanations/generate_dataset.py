import asyncio
import json
from pathlib import Path

import sys
sys.path.append("/media/main/Data/Abhijeet/Explanation_Dataset_Generation/Gemini-2.5-Pro/scripts/generate_gemini_dataset/common_scripts")
from logging_utils import Logger, LoggingStats
from process_mappings import run_pipeline

# ---- Tune these in one place (no hard-coded constants) ----
MAPPING_FILE = Path("/media/main/Data/Abhijeet/Datasets/MultiFakeVerse/mapping_files/generated_image_mappings/sampled_50_mappings.json")

RPM_PER_KEY = 5        # requests per minute for each key
RPD_PER_KEY = 100      # requests per day for each key
MAX_CONCURRENT = 20   # overall in-flight limit
SUCCESS_LOG_INTERVAL = 10

WAVE_SECONDS = 60      # 60 seconds per wave
ALIGN_TO_MINUTE = True # align first wave to the next :00
MAX_RETRIES_PER_ITEM = 0

PROMPT_TEMPLATE = "gemini_prompt_mark_5"
KEYS_CONFIG_PATH = "/media/main/Data/Abhijeet/Explanation_Dataset_Generation/config/keys.json"  # path to your keys.json

async def main():
    logger = Logger()
    logging_stats = LoggingStats(log_interval=SUCCESS_LOG_INTERVAL)
    mappings = json.loads(MAPPING_FILE.read_text(encoding="utf-8"))
    await run_pipeline(
        mappings=mappings,
        logger=logger,
        logging_stats=logging_stats,
        prompt_template=PROMPT_TEMPLATE,
        rpm_per_key=RPM_PER_KEY,
        rpd_per_key=RPD_PER_KEY,
        max_concurrent=MAX_CONCURRENT,
        wave_seconds=WAVE_SECONDS,
        align_to_minute=ALIGN_TO_MINUTE,
        max_retries_per_item=MAX_RETRIES_PER_ITEM,
        keys_config_path=KEYS_CONFIG_PATH,
    )

if __name__ == "__main__":
    asyncio.run(main())
