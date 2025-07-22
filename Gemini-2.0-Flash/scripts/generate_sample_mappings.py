import json
import random
from collections import defaultdict
from pathlib import Path

# Load the full mapping
base_path = Path("/media/main/Data/Abhijeet/Datasets/MultiFakeVerse")
mapping_file = base_path / "image_mappings.json"
output_path = base_path / "sample_mappings.json"

all_mappings = json.loads(mapping_file.read_text(encoding="utf-8"))

# Group entries by category key
groups = defaultdict(list)
for idx, entry in enumerate(all_mappings):
    key = (
        entry["generation_model"],
        entry["edit_suggestion_model"],
        entry["dataset"]
    )
    groups[key].append(idx)

# Uniform sampling per group
per_group = max(1, 50 // len(groups))
selected = []
for idx_list in groups.values():
    selected.extend(random.sample(idx_list, min(per_group, len(idx_list))))

# Fill up to 50 with random remaining entries
remaining = list(set(range(len(all_mappings))) - set(selected))
to_add = min(50 - len(selected), len(remaining))
if to_add > 0:
    selected.extend(random.sample(remaining, to_add))

# Build sampled entries
sampled_entries = [all_mappings[i] for i in selected]

# Sort entries for readability
sampled_entries.sort(key=lambda x: (
    x["generation_model"].casefold(),
    x["edit_suggestion_model"].casefold(),
    x["dataset"].casefold(),
    x["image_name"].casefold(),
    x["image_index"]
))

# Save the sampled mapping
output_path.write_text(json.dumps(sampled_entries, indent=2, ensure_ascii=False))

print(f"Sampled {len(sampled_entries)} entries across {len(groups)} categories.")
