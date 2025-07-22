import os
import asyncio
import sys
from pathlib import Path
import json
from google import genai
from PIL import Image
import re
from google.genai import types
from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from explanation_generation_prompts import PROMPTS

client = genai.Client(api_key=os.getenv("GOOGLE_GENAI_BILLED_API_KEY"))
MODEL = "gemini-2.0-flash"

def clean_response_text(text: str) -> str:
    text = text.strip()
    # Remove leading ```json or ``` and trailing ```
    # Regex matches the first fenced block and captures inner JSON
    match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', text, flags=re.DOTALL)
    if match:
        return match.group(1).strip()
    # Fallback: return as-is
    return text

async def get_explanation_async(
        gen_img: Image.Image, real_img: Image.Image, effect: dict, 
        prompt_name: str = "gemini_prompt_mark_2"
) -> dict:
    PROMPT_TEMPLATE = PROMPTS[prompt_name]
    if PROMPT_TEMPLATE is None:
        raise ValueError(f"Unknown prompt: {prompt_name}")
    effect_json=json.dumps(effect, ensure_ascii=False)
    prompt = PROMPT_TEMPLATE.substitute(effect_json=effect_json)

    for attempt in range(3):
        try:
            resp = await client.aio.models.generate_content(
                model=MODEL,
                contents=[real_img, gen_img, prompt]
            )
        except (ResourceExhausted, ServiceUnavailable) as e:
            backoff = 2 ** attempt
            print(f"[API retry] Attempt {attempt+1} in {backoff}s due to {e.code}")
            await asyncio.sleep(backoff)
            continue

        raw_output = resp.text
        clean_output = clean_response_text(raw_output)
        if not clean_output:
            print(f"[API retry] Empty response on attempt {attempt+1}. Retrying.")
            await asyncio.sleep(2 ** attempt)
            continue

        try:
            return json.loads(clean_output)
        except json.JSONDecodeError as e:
            print(f"[API retry] JSON parse error on attempt {attempt+1}: {e}. Raw: {clean_output[:200]!r}")
            await asyncio.sleep(2 ** attempt)
            continue

    # After retries exhausted:
    raise RuntimeError("Failed to get a valid JSON response from Gemini after 3 attempts")
