import os
from PIL import Image

RAW_DIR = "data/real/raw"
MAX_SIZE = (300, 300)

def resize_images():
    for f in os.listdir(RAW_DIR):
        if not f.endswith(".png"):
            continue
            
        path = os.path.join(RAW_DIR, f)
        try:
            with Image.open(path) as img:
                if img.width > MAX_SIZE[0] or img.height > MAX_SIZE[1]:
                    img.thumbnail(MAX_SIZE, Image.Resampling.LANCZOS)
                    img.save(path, "PNG")
                    print(f"Resized {f}")
        except Exception as e:
            print(f"Error resizing {f}: {e}")

if __name__ == "__main__":
    resize_images()
