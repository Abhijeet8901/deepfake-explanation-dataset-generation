import asyncio
import json
from pathlib import Path
from PIL import Image
from process_mappings import run_processing
from logging_utils import Logger

MAPPING_FILE = Path("/media/main/Data/Abhijeet/Datasets/MultiFakeVerse/sample_mappings.json")
RPM = 13
MAX_CONCURRENT = 200
SUCCESS_LOG_INTERVAL = 10
PROMPT_TEMPLATE = "gemini_prompt_mark_3" 

async def main():
    logger = Logger()
    mappings = json.loads(MAPPING_FILE.read_text(encoding="utf-8"))
    await run_processing(mappings, logger, prompt_template = PROMPT_TEMPLATE, rpm = RPM, max_concurrent = MAX_CONCURRENT, success_log_interval = SUCCESS_LOG_INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())
