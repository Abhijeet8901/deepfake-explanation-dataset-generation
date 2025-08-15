import json
from pathlib import Path

path = Path("/media/main/Data/Abhijeet/Explanation_Dataset_Generation/Gemini-2.0-Flash/Qwen Mappings/120k_dataset/qwen_train_mappings.json")

with open(path, "r") as f:
    data = json.load(f)

real_count = 0
tampered_count =0

for item in data:
    if(item['label'] == 'Real'):
        real_count += 1
        if(not Path(item['image_path']).exists()):
            print(f"Real image path does not exist: {item['image_path']}")
    elif(item['label'] == 'Tampered'):
        tampered_count += 1
        if(not Path(item['generated_image_path']).exists()):
            print(f"Generated image path does not exist: {item['generated_image_path']}")
        if(not Path(item['real_image_path']).exists()):
            print(f"Real image path does not exist: {item['real_image_path']}")
        if(not Path(item['explanation_path']).exists()):
            print(f"Edit suggestion path does not exist: {item['explanation_path']}")      

print(real_count, tampered_count)   

