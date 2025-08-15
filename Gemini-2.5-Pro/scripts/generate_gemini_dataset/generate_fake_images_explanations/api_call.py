import json
import re
from typing import Any, Dict
from PIL import Image
from google.genai import types
from google.genai.types import SafetySetting, HarmCategory, HarmBlockThreshold
import sys

# If you import from your project tree, keep this as-is.
# sys.path.append(...)  # if needed in your environment
sys.path.append("/media/main/Data/Abhijeet/Explanation_Dataset_Generation/Prompts")
from explanation_generation_prompts import GEMINI_PROMPTS  # assumes you have this

MODEL = "gemini-2.5-pro"

safety_settings = [
    SafetySetting(category=HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                  threshold=HarmBlockThreshold.BLOCK_NONE),
    SafetySetting(category=HarmCategory.HARM_CATEGORY_HARASSMENT,
                  threshold=HarmBlockThreshold.BLOCK_NONE),
    SafetySetting(category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                  threshold=HarmBlockThreshold.BLOCK_NONE),
    SafetySetting(category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                  threshold=HarmBlockThreshold.BLOCK_NONE),
    SafetySetting(category=HarmCategory.HARM_CATEGORY_CIVIC_INTEGRITY,
                  threshold=HarmBlockThreshold.BLOCK_NONE),
]

def _clean_response_text(text: str) -> str:
    text = text.strip()
    match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', text, flags=re.DOTALL)
    if match:
        return match.group(1).strip()
    return text

async def get_explanation_async(
    client: Any,
    gen_img: Image.Image,
    real_img: Image.Image,
    effect: Dict,
    prompt_name: str
) -> Dict:
    """
    One API call using a given client (already bound to a specific key).
    """
    tmpl = GEMINI_PROMPTS[prompt_name]
    if tmpl is None:
        raise ValueError(f"Unknown prompt: {prompt_name}")

    effect_json = json.dumps(effect, ensure_ascii=False)
    prompt = tmpl.substitute(effect_json=effect_json)

    resp = await client.aio.models.generate_content(
        model=MODEL,
        contents=[real_img, gen_img, prompt],
        config=types.GenerateContentConfig(safety_settings=safety_settings)
    )
    raw = resp.text or ""
    cleaned = _clean_response_text(raw)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # bubble up; scheduler will retry according to policy
        raise
