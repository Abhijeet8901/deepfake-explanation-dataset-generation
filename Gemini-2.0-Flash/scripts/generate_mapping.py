import json
from pathlib import Path

# Define root paths
base_path = Path("/media/main/Data/Abhijeet/Datasets/MultiFakeVerse")
real_images_path = base_path / "real_images"
edit_suggestions_path = base_path / "edit_suggestions"
generated_images_path = base_path / "generated_images"
output_json_path = base_path / "image_mappings.json"

# Init
mappings = []

# Traverse generation models
for generation_model_dir in generated_images_path.iterdir():
    if not generation_model_dir.is_dir():
        continue
    generation_model = generation_model_dir.name  # e.g. gemini_images

    for subfolder in generation_model_dir.iterdir():
        if not subfolder.is_dir():
            continue

        # Parse edit_suggestion_model and dataset from folder name
        # e.g. chatgpt-4o-latest_PIC_2.0 → chatgpt-4o-latest, PIC_2.0
        parts = subfolder.name.split("_", 1)
        if len(parts) != 2:
            print(f"Skipping malformed folder: {subfolder}")
            continue
        edit_suggestion_model, dataset = parts

        count = 0

        for gen_image in subfolder.glob("*.jpg"):
            stem = gen_image.stem  # e.g., image1_0
            try:
                image_base, image_index = stem.rsplit("_", 1)
            except ValueError:
                print(f"Skipping malformed filename: {gen_image.name}")
                continue

            try:
                image_index = int(image_index)
            except ValueError:
                print(f"Non-numeric index in filename: {gen_image.name}")
                continue

            real_image_path = real_images_path / dataset / f"{image_base}.jpg"
            edit_suggestion_path = edit_suggestions_path / f"{edit_suggestion_model}_{dataset}" / f"{image_base}.jpg.json"
            
            # Check existence
            if not real_image_path.exists():
                print(f"Missing real image for {gen_image.name}: {real_image_path}")
                continue
            if not edit_suggestion_path.exists():
                print(f"Missing edit suggestion for {gen_image.name}: {edit_suggestion_path}")
                continue

            # Load and validate edit_suggestion structure
            # try:
            #     with open(edit_suggestion_path, "r", encoding="utf-8") as f:
            #         suggestion_data = json.load(f)
            #         effects = suggestion_data.get("Effects", [])
            #         if not isinstance(effects, list):
            #             print(f"'Effects' field not a list in: {edit_suggestion_path}")
            #             continue
            #         if image_index >= len(effects):
            #             print(f"Image index {image_index} out of bounds for Effects in: {edit_suggestion_path}")
            #             continue
            # except Exception as e:
            #     print(f"Error reading edit_suggestion {edit_suggestion_path}: {e}")
            #     continue

            output_explanation_path = (
                Path("Generated Explanations") /
                "Gemini-2.0-Flash" /
                generation_model /
                f"{edit_suggestion_model}_{dataset}"
            )
            output_explanation_name = gen_image.stem + ".json"

            mappings.append({
                "generation_model": generation_model,
                "edit_suggestion_model": edit_suggestion_model,
                "dataset": dataset,
                "image_name": image_base,
                "image_index": image_index,
                "generated_image_path": str(gen_image),
                "real_image_path": str(real_image_path),
                "edit_suggestion_path": str(edit_suggestion_path),
                "output_explanation_path": str(output_explanation_path),
                "output_explanation_name": output_explanation_name
            })
            count += 1

        # Print progress for this subfolder
        print(f"Processed {count} images in {generation_model}/{subfolder.name}")            

# Sort mappings by the full folder hierarchy
mappings.sort(key=lambda x: (
    x["generation_model"].casefold(),
    x["edit_suggestion_model"].casefold(),
    x["dataset"].casefold(),
    x["image_name"].casefold(),
    x["image_index"]
))

# Save mapping
with open(output_json_path, "w") as f:
    json.dump(mappings, f, indent=2)

print(f"Saved {len(mappings)} mappings to {output_json_path}")
