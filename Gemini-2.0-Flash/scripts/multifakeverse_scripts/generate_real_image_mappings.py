import json
from pathlib import Path

# Define root paths
base_path = Path("/media/main/Data/Abhijeet/Datasets/MultiFakeVerse")
real_images_path = base_path / "real_images"
edit_suggestions_path = base_path / "edit_suggestions"
generated_images_path = base_path / "generated_images"
output_json_path = base_path / "mapping_files" / "real_image_mappings" / "complete_mappings.json"

# Init
mappings = []

# Traverse generation models
for subfolder in real_images_path.iterdir():
    if not subfolder.is_dir():
        continue

    dataset = subfolder.name 
    count = 0

    for real_image in subfolder.glob("*.jpg"):
        image_name = real_image.stem 

        output_explanation_path = (
            Path("/media/main/Data/Abhijeet/Explanation_Dataset_Generation/Real Image Explanations") /
            "Gemini-2.0-Flash" /
            dataset
        )
        output_explanation_name = image_name + ".json"

        mappings.append({
            "dataset": dataset,
            "image_name": image_name,
            "real_image_path": str(real_image),
            "output_explanation_path": str(output_explanation_path),
            "output_explanation_name": output_explanation_name
        })
        count += 1

    # Print progress for this subfolder
    print(f"Processed {count} images in {dataset}")   

# Sort mappings by the full folder hierarchy
mappings.sort(key=lambda x: (
    x["dataset"].casefold(),
    x["image_name"].casefold(),
))

output_json_path.parent.mkdir(parents=True, exist_ok=True)
# Save mapping
with open(output_json_path, "w") as f:
    json.dump(mappings, f, indent=2)

print(f"Saved {len(mappings)} mappings to {output_json_path}")
