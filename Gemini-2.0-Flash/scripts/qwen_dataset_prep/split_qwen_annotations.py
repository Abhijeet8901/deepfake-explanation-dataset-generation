import json
import random
from pathlib import Path

SOURCE_JSONL = Path("/media/main/Data/Abhijeet/Explanation_Dataset_Generation/Gemini-2.0-Flash/Qwen Mappings/120k_dataset/qwen_annotations.jsonl")

OUT_DIR = SOURCE_JSONL.parent
VAL_REAL = 10000
VAL_TAMPERED = 10000
SEED = 5318008

# 1 ─── read & bucket ────────────────────────────────────────────────────────
real, tampered = [], []
with SOURCE_JSONL.open() as f:
    for line in f:
        obj = json.loads(line)
        if obj["suffix"]["verdict"] == "Real":
            real.append(obj)
        else:
            tampered.append(obj)

print(f"✅ read {len(real):,} Real and {len(tampered):,} Tampered")
# assert len(real) == 45000 and len(tampered) == 45000, "Counts mismatch!"

# 2 ─── shuffle deterministically ───────────────────────────────────────────
random.seed(SEED)
random.shuffle(real)
random.shuffle(tampered)

# 3 ─── slice validation + training sets ────────────────────────────────────
val = real[:VAL_REAL] + tampered[:VAL_TAMPERED]
train = real[VAL_REAL:] + tampered[VAL_TAMPERED:]

# 4 ─── re-shuffle each split so classes mix well ───────────────────────────
random.shuffle(val)
random.shuffle(train)

# 5 ─── write jsonl files ───────────────────────────────────────────────────
def write_jsonl(path, rows):
    with path.open("w", encoding="utf-8") as f:
        for obj in rows:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")

write_jsonl(OUT_DIR / "qwen_val_annotations.jsonl",   val)
write_jsonl(OUT_DIR / "qwen_train_annotations.jsonl", train)

print("✅  wrote",
      f"{len(train):,} train rows and {len(val):,} val rows to {OUT_DIR}")
