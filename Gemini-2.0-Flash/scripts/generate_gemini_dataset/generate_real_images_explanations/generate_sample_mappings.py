import json
import random
from pathlib import Path

# Config
mapping_file_path = Path("/media/main/Data/Abhijeet/Datasets/MultiFakeVerse/mapping_files/real_image_mappings/complete_mappings.json")
output_sample_path = mapping_file_path.parent / "sampled_50_mappings.json"

# Load all mappings
with open(mapping_file_path, "r") as f:
    mappings = json.load(f)

# Check total available
total_mappings = len(mappings)
print(f"Total mappings found: {total_mappings}")

# Sample 50 random entries (or fewer if not enough)
sample_size = min(50, total_mappings)
sampled = random.sample(mappings, sample_size)

# Save the sampled entries
with open(output_sample_path, "w") as f:
    json.dump(sampled, f, indent=2)

print(f"Saved {sample_size} random mappings to {output_sample_path}")
