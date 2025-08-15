import json, uuid, argparse
from pathlib import Path
from tqdm import tqdm
from datasets import Dataset
from collections import OrderedDict
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from Explanation_Dataset_Generation.Prompts.explanation_generation_prompts import QWEN_PROMPTS

TRAIN_DATASET_MAPPINGS_PATH = "/media/main/Data/Abhijeet/Explanation_Dataset_Generation/Gemini-2.0-Flash/qwen_train_mappings.json"
OUTPUT_QWEN_TRAIN_DATA_PATH = "/media/main/Data/Abhijeet/Explanation_Dataset_Generation/Gemini-2.0-Flash/qwen_train_data.json"

PROMPT = QWEN_PROMPTS["qwen_user_prompt_mark_1"]
SYSTEM = QWEN_PROMPTS["qwen_system_prompt"]

# helper so every record has all four keys
BLANK_ASSIST = {
    "manipulation_analysis": [],
    "inferred_original_state": {},
    "inverse_edit_instruction": {},
}

def load_json(p):
    with open(p, "r") as f:
        return json.load(f)

def build_record(m):
    if m["label"].lower() == "real":
        img_path = m["image_path"]

        assistant = OrderedDict([
            ("verdict", "Real"),
            ("manipulation_analysis", []),
            ("inferred_original_state", {}),
            ("inverse_edit_instruction", {})
        ])

    else:  # Tampered
        img_path = m["generated_image_path"]
        src = load_json(m["explanation_path"])

        # Fill any gaps, then reorder keys
        manip = src.get("manipulation_analysis", [])
        orig  = src.get("inferred_original_state", {})
        inv   = src.get("inverse_edit_instruction", {})

        assistant = OrderedDict([
            ("verdict", "Tampered"),
            ("manipulation_analysis", manip),
            ("inferred_original_state", orig),
            ("inverse_edit_instruction", inv)
        ])

    uid = f'{m.get("dataset","NA")}_{m["image_name"]}_{m.get("image_index",0)}'

    return {
        "id": uid,
        "conversations": [
            { "role": "system",
              "content": [ {"type": "text", "text": SYSTEM} ] },

            { "role": "user",
              "content": [
                  {"type": "image", "image": img_path},
                  {"type": "text",  "text": PROMPT}
              ] },

            { "role": "assistant",
              "content": [
                  { "type": "text",
                    "text": json.dumps(assistant, ensure_ascii=False,
                                       separators=(",",":")) }
              ] }
        ]
    }

def main():
    mapping  = load_json(TRAIN_DATASET_MAPPINGS_PATH)
    records  = [build_record(x) for x in tqdm(mapping, desc="Building")]
    out_path = Path(OUTPUT_QWEN_TRAIN_DATA_PATH); out_path.parent.mkdir(exist_ok=True, parents=True)
    out_path.write_text(json.dumps(records, ensure_ascii=False, indent=2))
    print(f"✓ wrote {len(records):,} samples to {out_path}")

if __name__ == "__main__":
    main()
