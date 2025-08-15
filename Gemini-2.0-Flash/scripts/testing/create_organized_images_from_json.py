import os
import shutil
import json

def organize_files(mappings, dest_root):
    """
    mappings: list of dicts as in your JSON file
    dest_root: base directory to copy into
    """
    for m in mappings:
        dataset = f"{m['dataset']}"
        subdir = os.path.join(dest_root, dataset)
        os.makedirs(subdir, exist_ok=True)

        copies = [("real_image_path", os.path.basename(m["real_image_path"]))]

        for key, filename in copies:
            src = m[key]
            dst = os.path.join(subdir, filename)
            try:
                shutil.copy2(src, dst)
                print(f"Copied {src} → {dst}")
            except FileNotFoundError:
                print(f"⚠️ Missing file: {src}")
            except Exception as e:
                print(f"Error copying {src} → {dst}: {e}")

if __name__ == "__main__":
    import json
    with open("/media/main/Data/Abhijeet/Datasets/MultiFakeVerse/mapping_files/real_image_mappings/sampled_50_mappings.json") as f:
        mappings = json.load(f)

    organize_files(mappings, dest_root="/media/main/Data/Abhijeet/Explanation_Dataset_Generation/Sample Real Image Explanations/Sample Images")
