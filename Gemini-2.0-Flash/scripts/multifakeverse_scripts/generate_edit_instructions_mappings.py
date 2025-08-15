import json
from pathlib import Path

# Define root paths
base_path = Path("/media/main/Data/Abhijeet/Datasets/MultiFakeVerse")
edit_suggestions_path = base_path / "additional_edit_instructions" / "Gemini-2.0-Flash"
real_images_folder = base_path / "real_images"
output_json_path = base_path / "mapping_files" / "additional_edit_instructions_to_generated_image_mappings" / "complete_mappings.json"

# Init
mappings = []

# Traverse generation models
for subfolder in edit_suggestions_path.iterdir():
    if not subfolder.is_dir():
        continue

    dataset = subfolder.name 
    count = 0
    total_count = 0

    for edit_suggestion_path in subfolder.glob("*.json"):
        image_name = edit_suggestion_path.stem 

        with open(edit_suggestion_path, "r") as f:
            edit_suggestion_data = json.load(f)

        edit_suggestion_data = edit_suggestion_data.get("manipulations", {})

        # if(len(edit_suggestion_data) != 5):
        #     print(f"Edit suggestion for {image_name} does not have exactly 5 manipulations: {len(edit_suggestion_data)}")

        real_image_path = real_images_folder / dataset / f"{image_name}.jpg"

        if not real_image_path.exists():
            print(f"Missing real image for {image_name}: {real_image_path}")
            continue
        if not edit_suggestion_path.exists():
            print(f"Missing edit suggestion for {image_name}: {edit_suggestion_path}")
            continue
        for index, edit_suggestion in enumerate(edit_suggestion_data):
            output_generated_image_path = (
                Path("/media/main/Data/Abhijeet/Datasets/MultiFakeVerse/additional_generated_images") /
                dataset /
                f"{image_name}_{index}.jpg"
            )
            mappings.append({
                "dataset": dataset,
                "image_name": image_name,
                "index": index,
                "real_image_path": str(real_image_path),
                "output_generated_image_path": str(output_generated_image_path)
            })
            total_count += 1

        count += 1

    # Print progress for this subfolder
    print(f"Processed {count} images in {dataset}")
    print(f"Total processed edits {total_count} in {dataset}")   

# Sort mappings by the full folder hierarchy
mappings.sort(key=lambda x: (
    x["dataset"].casefold(),
    x["image_name"].casefold(),
    x["index"]
))

output_json_path.parent.mkdir(parents=True, exist_ok=True)
# Save mapping
# with open(output_json_path, "w") as f:
#     json.dump(mappings, f, indent=2)

print(f"Saved {len(mappings)} mappings to {output_json_path}")
