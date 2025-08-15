import random
import json
from pathlib import Path

# Config
BASE = Path("/media/main/Data/Abhijeet/Datasets/MultiFakeVerse")
real_root = BASE / "real_images"
generated_root = BASE / "generated_images"
OUTPUT_PATH = Path("/media/main/Data/Abhijeet/Explanation_Dataset_Generation/Gemini-2.0-Flash/Qwen Mappings/120k_dataset/qwen_train_mappings.json")
EXPLANATION_PATH = Path("/media/main/Data/Abhijeet/Explanation_Dataset_Generation/Generated Explanations/Gemini-2.0-Flash")

TRAIN_SET_LEN = 80000
SET1_LEN = 40000 # Images whose deepfakes will be used
SET2_LEN = TRAIN_SET_LEN - SET1_LEN # Images whose deepfakes won't be used. 
DEEPFAKE_IMAGES_LEN = 60000
SET1_DUPLICATES = DEEPFAKE_IMAGES_LEN - SET1_LEN  
SET1_ONES = SET1_LEN - SET1_DUPLICATES  # rest get only one

random.seed(5318008)

def list_all_reals(root):
    return [p for ds in root.iterdir() if ds.is_dir() for p in ds.glob("*.jpg")]

# All real images
all_reals = list_all_reals(real_root)
assert len(all_reals) >= TRAIN_SET_LEN, "Not enough real images!"

train_images = random.sample(all_reals, TRAIN_SET_LEN)
set1_images = train_images[:SET1_LEN]
set2_images = train_images[SET1_LEN:]

with open("/media/main/Data/Abhijeet/Datasets/MultiFakeVerse/image_mappings.json") as f:
    mappings = json.load(f)

set1_mappings = random.sample(mappings, DEEPFAKE_IMAGES_LEN)
set1_real_images_list = []
for rm in set1_mappings:
    real_image = rm["real_image_path"]
    set1_real_images_list.append(real_image)

set1_real_images = list(set(set1_real_images_list))

real_images_with_no_deepfakes_len = TRAIN_SET_LEN - len(set1_real_images)
real_images_with_deepfakes_len = DEEPFAKE_IMAGES_LEN - real_images_with_no_deepfakes_len

real_images_with_no_deepfake_total = list(set(all_reals) - set(set1_real_images))

real_images_with_no_deepfakes = random.sample(real_images_with_no_deepfake_total, real_images_with_no_deepfakes_len)
real_images_with_deepfakes = random.sample(set1_real_images, real_images_with_deepfakes_len)

final_real_images_for_train = (real_images_with_deepfakes + real_images_with_no_deepfakes)

final_real_images_for_train = list(set(final_real_images_for_train))
final_deepfake_images_for_train = set1_mappings

random.shuffle(final_real_images_for_train)
random.shuffle(final_deepfake_images_for_train)

final_deepfake_image_mappings = []
final_real_image_mappings = [] 
for deepfake_mapping in final_deepfake_images_for_train:
    generated_image_path = Path(deepfake_mapping["generated_image_path"])
    last_three = Path(*generated_image_path.parts[-3:]).with_suffix(".json")    
    final_deepfake_image_mappings.append({
        "label": "Tampered",
        "generation_model": deepfake_mapping["generation_model"],
        "edit_suggestion_model": deepfake_mapping["edit_suggestion_model"],
        "dataset": deepfake_mapping["dataset"],
        "image_name": deepfake_mapping["image_name"],
        "image_index": deepfake_mapping["image_index"],
        "generated_image_path": deepfake_mapping["generated_image_path"],
        "real_image_path": deepfake_mapping["real_image_path"],
        "explanation_path": str(EXPLANATION_PATH / last_three)
    })

for curr_real_image_path in final_real_images_for_train:
    final_real_image_mappings.append({
        "label": "Real",
        "dataset": str(Path(curr_real_image_path).parts[-2]),
        "image_name": str(Path(curr_real_image_path).stem.rsplit("_", 1)[0]),
        "image_path": str(curr_real_image_path)
    })

training_mappings = final_real_image_mappings + final_deepfake_image_mappings

random.shuffle(training_mappings)

with open(OUTPUT_PATH, "w") as f:
    json.dump(training_mappings, f, indent=2)