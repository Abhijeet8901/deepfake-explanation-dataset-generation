from pathlib import Path
import json

base_path = Path("/media/main/Data/Abhijeet/Datasets/MultiFakeVerse")
edit_instructions_path = base_path / "additional_edit_instructions_old" / "Gemini-2.0-Flash"
new_edit_instructions_path = base_path / "additional_edit_instructions" / "Gemini-2.0-Flash"

for subfolder in edit_instructions_path.iterdir():
    if not subfolder.is_dir():
        continue
    
    dataset = subfolder.name 
    count = 0
    
    for edit_suggestion in subfolder.glob("*.json"):
        with open(edit_suggestion, "r") as f:
            edit_suggestion_data = json.load(f)

        edit_suggestion_data["manipulations"] = [{k: v} for k, v in edit_suggestion_data["manipulations"].items()]
        new_edit_suggestion_path = new_edit_instructions_path / dataset / edit_suggestion.name 
        new_edit_suggestion_path.parent.mkdir(parents=True, exist_ok=True)
        with open(new_edit_suggestion_path, "w") as f:
            json.dump(edit_suggestion_data, f, indent=4)
        count += 1  

    # Print progress for this subfolder
    print(f"Processed {count} images in {dataset}")              

