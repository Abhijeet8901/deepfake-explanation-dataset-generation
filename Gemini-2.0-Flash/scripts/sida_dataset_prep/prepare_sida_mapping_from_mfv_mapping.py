import json
from pathlib import Path
import random

SEED = random.seed(5318008) 

TYPE = "train"
FILE_NAME = TYPE + "_mappings.json"
INPUT_BASE_PATH = Path("/media/main/Data/Abhijeet/Datasets/MultiFakeVerse/mapping_files")
INPUT_PATH = INPUT_BASE_PATH / FILE_NAME

SPLITS_FILE_PATH = INPUT_BASE_PATH / "splits.json"

OUTPUT_BASE_PATH = Path("/media/main/Data/Abhijeet/Explanation_Dataset_Generation/Gemini-2.0-Flash/SIDA Mappings/full_dataset")
OUTPUT_PATH = OUTPUT_BASE_PATH / ("sida_" + FILE_NAME)

EXPLANATION_DIR_PATH = Path("/media/main/Data/Abhijeet/Explanation_Dataset_Generation/Generated Explanations/Gemini-2.0-Flash")

MASK_DIR_PATH = Path("/media/main/Data/Abhijeet/Datasets/MultiFakeVerse/generated_images_masks")

with open(INPUT_PATH) as f:
    image_mappings = json.load(f)

with open(SPLITS_FILE_PATH) as f:
    split_mappings = json.load(f)

print(f"Total Tampered images in {TYPE} mappings: {len(image_mappings)}")

generated_image_mappings = []
for index, mapping in enumerate(image_mappings):
    generated_image_path = Path(mapping["generated_image_path"])
    last_three = Path(*generated_image_path.parts[-3:]).with_suffix(".json")
    explanation_path = EXPLANATION_DIR_PATH / last_three

    dataset = mapping["dataset"]
    edit_suggestion_model = mapping["edit_suggestion_model"].split("-")[0]
    if edit_suggestion_model == "gemini":
        edit_suggestion_model = "geminiflash"
    generation_model = mapping["generation_model"]
    mask_path = MASK_DIR_PATH / (generation_model + "_masks") / (dataset + "_" +edit_suggestion_model) / generated_image_path.name  
    
    if( not explanation_path.exists()):
        print(f"Explanation file does not exist for {mapping['generated_image_path']}")
        continue
    if(not Path(mapping["real_image_path"]).exists()):
        print(f"Real image path is missing for {mapping['generated_image_path']}")
        continue
    if(not Path(mapping["generated_image_path"]).exists()):
        print(f"Generated image file is missing for {mapping['generated_image_path']}")
        continue
    if(not mask_path.exists()):
        print(f"Mask file is missing for {mask_path}")
        continue                  
    generated_image_mappings.append({
        "label": "Tampered",
        "generation_model": mapping["generation_model"],
        "edit_suggestion_model": mapping["edit_suggestion_model"],
        "dataset": mapping["dataset"],
        "image_name": mapping["image_name"],
        "image_index": mapping["image_index"],
        "generated_image_path": mapping["generated_image_path"],
        "real_image_path": mapping["real_image_path"],
        "explanation_path": str(explanation_path),
        "mask_path": str(mask_path)
    })
    if index % 10000 == 0:
        print(f"Processed {index} mappings out of {len(image_mappings)}")

print(f"Total generated images: {len(generated_image_mappings)} out of {len(image_mappings)}")

real_image_mappings = []
REAL_IMAGES_BASE_PATH = Path("/media/main/Data/Abhijeet/Datasets/MultiFakeVerse/real_images")
for dataset in split_mappings[TYPE].keys():
    for image_name in split_mappings[TYPE][dataset]:
        real_image_path = REAL_IMAGES_BASE_PATH / dataset / image_name
        if(not real_image_path.exists()):
            print(f"Real image path is missing for {real_image_path}")
            continue
        real_image_mappings.append({
            "label": "Real",
            "dataset": str(real_image_path.parts[-2]),
            "image_name": str(real_image_path.stem),
            "image_path": str(real_image_path)
        }) 

print(f"Total real images: {len(real_image_mappings)}")

random.shuffle(generated_image_mappings)
random.shuffle(real_image_mappings)

completed_mappings = real_image_mappings + generated_image_mappings

random.shuffle(completed_mappings)

with open(OUTPUT_PATH, "w") as f:
    json.dump(completed_mappings, f, indent=2)

