import json, tqdm
from pathlib import Path
from collections import OrderedDict
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))
from Explanation_Dataset_Generation.Prompts.explanation_generation_prompts import QWEN_PROMPTS

MAP_FILE   = Path("/media/main/Data/Abhijeet/Explanation_Dataset_Generation/Gemini-2.0-Flash/Qwen Mappings/120k_dataset/qwen_train_mappings.json")   # your file
OUT_JSONL  = Path("/media/main/Data/Abhijeet/Explanation_Dataset_Generation/Gemini-2.0-Flash/Qwen Mappings/120k_dataset/qwen_annotations.jsonl")
PROMPT     = QWEN_PROMPTS["qwen_user_prompt_mark_2"]

rows = json.load(MAP_FILE.open())            # assumes list[…]
OUT_JSONL.parent.mkdir(parents=True, exist_ok=True)

def load_json(p):
    with open(p, "r") as f:
        return json.load(f)
    
def make_suffix(record):
    if record["label"] == "Real":
        return OrderedDict([
            ("verdict", "Real"),
            ("manipulation_analysis", []),
            ("inferred_original_state", {}),
            ("inverse_edit_instruction", {})
        ])
    else:
        src = load_json(record["explanation_path"])

        # Fill any gaps, then reorder keys
        manip = src.get("manipulation_analysis", [])
        orig  = src.get("inferred_original_state", {})
        inv   = src.get("inverse_edit_instruction", {})

        return OrderedDict([
            ("verdict", "Tampered"),
            ("manipulation_analysis", manip),
            ("inferred_original_state", orig),
            ("inverse_edit_instruction", inv)
        ])

with OUT_JSONL.open("w", encoding="utf-8") as out:
    for r in tqdm.tqdm(rows):
        img_key = "image_path" if r["label"] == "Real" else "generated_image_path"
        obj = {
            "image": r[img_key],         # keep absolute or make relative, up to you
            "prefix": PROMPT,
            "suffix": make_suffix(r)
        }
        out.write(json.dumps(obj, ensure_ascii=False) + "\n")

print("✅ wrote", OUT_JSONL)
