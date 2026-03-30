"""
Re-optimize non-hero images from 1200px max → 800px max, quality 75.
Hero slider images are kept at 1200px (needed for desktop 960px slider).
"""
import glob, os
from PIL import Image

HERO_IMAGES = {
    "Images/opt/Prayer_Mandir/final/WhatsApp Image 2025-03-02 at 8.04.42 PM.webp",
    "Images/opt/Prayer_Havan Group/Final/Group Prayer.webp",
    "Images/opt/Yoga in Open Meditation Area/final/WhatsApp Image 2025-03-02 at 8.09.19 PM.webp",
    "Images/opt/Shaanti Puja/WhatsApp Image 2025-03-02 at 4.41.07 PM.webp",
    "Images/opt/Community Lunch/final/WhatsApp Image 2025-03-02 at 8.24.33 PM.webp",
}

MAX_SIZE = 800
QUALITY = 75

processed = skipped = already_small = 0
total_saved = 0

for path in glob.glob("Images/opt/**/*.webp", recursive=True):
    # Normalize to forward slashes for comparison
    norm = path.replace("\\", "/")
    if norm in HERO_IMAGES:
        skipped += 1
        continue

    orig_size = os.path.getsize(path)
    img = Image.open(path)
    w, h = img.size

    if max(w, h) <= MAX_SIZE:
        already_small += 1
        continue

    # Resize proportionally
    if w >= h:
        new_w = MAX_SIZE
        new_h = round(h * MAX_SIZE / w)
    else:
        new_h = MAX_SIZE
        new_w = round(w * MAX_SIZE / h)

    img = img.resize((new_w, new_h), Image.LANCZOS)
    img.save(path, "webp", quality=QUALITY, method=6)
    new_size = os.path.getsize(path)
    total_saved += orig_size - new_size
    processed += 1

print(f"Processed: {processed}")
print(f"Hero skipped: {skipped}")
print(f"Already small: {already_small}")
print(f"Total saved: {total_saved/1024/1024:.1f} MB")
