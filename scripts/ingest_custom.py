import os
import glob
from PIL import Image
import json

TRAIN_DIR = "train"
OUTPUT_DIR = "data/real/raw"
METADATA_PATH = "data/real/metadata/dataset.json"

def process():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(METADATA_PATH), exist_ok=True)
    
    images_metadata = []
    
    colors = ["red", "blue", "green", "yellow"]
    for color in colors:
        input_dir = os.path.join(TRAIN_DIR, color)
        if not os.path.exists(input_dir):
            continue
            
        files = [f for f in os.listdir(input_dir) if f != ".DS_Store"]
        for idx, f in enumerate(files):
            src_path = os.path.join(input_dir, f)
            base_name = f"real_{color}_{idx+1}"
            dest_filename = f"{base_name}.png"
            dest_path = os.path.join(OUTPUT_DIR, dest_filename)
            
            try:
                with Image.open(src_path) as img:
                    # convert to RGB to avoid alpha channel issues with cv2
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    img.save(dest_path, "PNG")
                    
                record = {
                    "image_id": base_name,
                    "image_path": dest_path,
                    "target_color": color,
                    "expected_count": 1,  # PLACEHOLDER
                    "lighting": "controlled",
                    "background": "plain",
                    "overlap": "none",
                    "notes": f"Custom {color} images"
                }
                images_metadata.append(record)
                
            except Exception as e:
                print(f"Failed to process {f}: {e}")

    metadata = {
        "dataset_name": "custom-real-dataset",
        "metadata_schema_version": "v1",
        "profile_set_path": "configs/profiles/v1/multi-color-template.json",
        "images": images_metadata
    }
    
    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)
        
    print(f"Processed {len(images_metadata)} images.")

if __name__ == "__main__":
    process()
