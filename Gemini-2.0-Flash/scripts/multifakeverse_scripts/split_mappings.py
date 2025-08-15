import json
from pathlib import Path

base_path = Path("/media/main/Data/Abhijeet/Datasets/MultiFakeVerse/mapping_files")
complete_mappings_path = base_path / "complete_mappings.json"
splits_file_path = base_path / "splits.json"
output_train_path = base_path / "train_mappings.json"
output_val_path = base_path / "val_mappings.json"
output_test_path = base_path / "test_mappings.json"

with open(complete_mappings_path) as f:
    image_mappings = json.load(f)

with open(splits_file_path) as f:
    split_mappings = json.load(f)


train_mappings = []
val_mappings = []
test_mappings = []

total_images = len(image_mappings)

for index, mapping in enumerate(image_mappings):
    dataset = mapping["dataset"]
    image_name = mapping["image_name"]+".jpg"
    if(image_name in split_mappings["train"][dataset]):
        train_mappings.append(mapping)
    elif(image_name in split_mappings["val"][dataset]):
        val_mappings.append(mapping)
    elif(image_name in split_mappings["test"][dataset]):
        test_mappings.append(mapping)
    else:
        print(f"Image {image_name} not found in any split for dataset {dataset}"),
    if(index % 10000 == 0):
        print(f"Processed {index} out of {total_images} images")

with open(output_train_path, "w") as f:
    json.dump(train_mappings, f, indent=2)

print(f"Saved {len(train_mappings)} training mappings to {output_train_path}")

with open(output_val_path, "w") as f:
    json.dump(val_mappings, f, indent=2)

print(f"Saved {len(val_mappings)} validation mappings to {output_val_path}")

with open(output_test_path, "w") as f:
    json.dump(test_mappings, f, indent=2)

print(f"Saved {len(test_mappings)} test mappings to {output_test_path}")

