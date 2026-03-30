"""
Image optimization script for Prithvi Foundation website.
Converts JPEG/PNG images to WebP, resizes to appropriate display dimensions,
and saves optimized versions preserving folder structure.
"""
import os
import sys
from pathlib import Path
from PIL import Image

# Project root
ROOT = Path(__file__).parent

# Source → optimized output root
IMG_ROOT = ROOT / "Images"
OPT_ROOT = ROOT / "Images" / "opt"
LOGO_SRC = ROOT / "logo"
LOGO_OPT = ROOT / "logo" / "opt"

# Quality for WebP encoding (80 gives excellent visual quality at ~70% smaller size)
WEBP_QUALITY = 80

# Per-image max dimensions (width, height) — image is downsized to fit inside
# these bounds while preserving aspect ratio. Never upscale.
# Key is the relative path from IMG_ROOT (forward slashes, decoded).
SPECIFIC_SIZES = {
    "_DSC8795.jpg": (1600, 1100),   # hero image
}
# Default max size for all other images
DEFAULT_MAX = (1200, 1200)
# Max for logo
LOGO_MAX = (400, 200)


def resize_and_convert(src: Path, dst: Path, max_wh: tuple[int, int]) -> tuple[int, int, int]:
    """
    Open src image, downscale if larger than max_wh, save as WebP to dst.
    Returns (original_bytes, new_bytes, (w, h) of saved image).
    """
    dst.parent.mkdir(parents=True, exist_ok=True)

    img = Image.open(src)
    # Convert palette / RGBA modes to RGB for JPEG-compatible WebP
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGBA")  # keep alpha for PNG logos
    elif img.mode != "RGB":
        img = img.convert("RGB")

    orig_w, orig_h = img.size
    max_w, max_h = max_wh

    # Only downscale, never upscale
    scale = min(max_w / orig_w, max_h / orig_h, 1.0)
    new_w = int(orig_w * scale)
    new_h = int(orig_h * scale)

    if scale < 1.0:
        img = img.resize((new_w, new_h), Image.LANCZOS)

    # WebP saves RGBA fine; for RGB images use method=6 for better compression
    save_kwargs = {"format": "WEBP", "quality": WEBP_QUALITY, "method": 6}
    img.save(dst, **save_kwargs)

    orig_bytes = src.stat().st_size
    new_bytes = dst.stat().st_size
    return orig_bytes, new_bytes, (img.width, img.height)


def process_directory(src_root: Path, dst_root: Path, default_max: tuple[int, int]):
    total_orig = 0
    total_new = 0
    count = 0

    extensions = {".jpg", ".jpeg", ".png"}

    for src in sorted(src_root.rglob("*")):
        if not src.is_file():
            continue
        if src.suffix.lower() not in extensions:
            continue
        # Skip already-optimized outputs
        if "opt" in src.parts:
            continue

        # Relative path from src_root
        rel = src.relative_to(src_root)
        dst = dst_root / rel.with_suffix(".webp")

        # Pick size override if available
        max_wh = SPECIFIC_SIZES.get(src.name, default_max)

        orig_kb = src.stat().st_size / 1024
        orig_b, new_b, dims = resize_and_convert(src, dst, max_wh)
        saved_kb = (orig_b - new_b) / 1024

        total_orig += orig_b
        total_new += new_b
        count += 1

        status = "✓" if new_b < orig_b else "!"
        print(f"  {status} {rel.as_posix()}")
        print(f"      {orig_b/1024:.0f} KB → {new_b/1024:.0f} KB  ({dims[0]}×{dims[1]})  saved {saved_kb:.0f} KB")

    return total_orig, total_new, count


def main():
    print("=" * 70)
    print("Optimizing Images/  →  Images/opt/")
    print("=" * 70)
    orig, new, n = process_directory(IMG_ROOT, OPT_ROOT, DEFAULT_MAX)
    print()
    print("=" * 70)
    print("Optimizing logo/  →  logo/opt/")
    print("=" * 70)
    orig2, new2, n2 = process_directory(LOGO_SRC, LOGO_OPT, LOGO_MAX)

    total_orig = orig + orig2
    total_new = new + new2
    total_n = n + n2
    saved = total_orig - total_new

    print()
    print("=" * 70)
    print(f"DONE  {total_n} images processed")
    print(f"  Total original : {total_orig/1024/1024:.1f} MB")
    print(f"  Total optimized: {total_new/1024/1024:.1f} MB")
    print(f"  Total saved    : {saved/1024/1024:.1f} MB  ({saved/total_orig*100:.0f}% reduction)")
    print("=" * 70)


if __name__ == "__main__":
    main()
