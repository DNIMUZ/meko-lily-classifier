"""Prepare cat photos for a public repository.

What it does:
1. Backs up the original raw photos into ``data/originals/`` (gitignored).
2. Re-encodes every image in ``data/cats/``: RGB, longest side capped at
   ``MAX_SIZE``, EXIF/GPS stripped, saved as JPEG (quality ``JPEG_QUALITY``).
3. Lowercases every file extension.
4. Caps the ``other`` class to ``OTHER_MAX`` random samples and flattens them
   into ``data/cats/other/`` with unique, human-readable names.

The processed files in ``data/cats/`` are the only ones committed to Git.
"""

import os
import random
import re
import shutil
from pathlib import Path

from PIL import Image, ImageOps

PROJECT_DIR = Path(__file__).parent
DATA_DIR = PROJECT_DIR / "data" / "cats"
BACKUP_DIR = PROJECT_DIR / "data" / "originals"

MAX_SIZE = 448
JPEG_QUALITY = 85
OTHER_MAX = 1000
SEED = 42
IMAGE_EXTS = {".jpg", ".jpeg", ".png"}

random.seed(SEED)


def is_image(path: Path) -> bool:
    return path.suffix.lower() in IMAGE_EXTS


def process_one(src: Path, dst: Path) -> None:
    """Re-encode ``src`` into ``dst``, stripping EXIF and capping resolution."""
    with Image.open(src) as im:
        transposed = ImageOps.exif_transpose(im)
        image = transposed.convert("RGB")
        image.thumbnail((MAX_SIZE, MAX_SIZE))
        tmp = dst.with_suffix(dst.suffix + ".tmp")
        image.save(tmp, "JPEG", quality=JPEG_QUALITY)
    os.replace(tmp, dst)


def backup_images(file_list, backup_dir: Path, relative_to: Path | None = None) -> None:
    backup_dir.mkdir(parents=True, exist_ok=True)
    for path in file_list:
        if relative_to is not None:
            dst = backup_dir / path.relative_to(relative_to)
        else:
            dst = backup_dir / path.name
        if not dst.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dst)


def folder_counts() -> dict:
    counts = {}
    for class_dir in sorted(DATA_DIR.iterdir()):
        if not class_dir.is_dir() or class_dir.name.startswith("."):
            continue
        counts[class_dir.name] = sum(1 for p in class_dir.rglob("*") if is_image(p))
    return counts


def process_meko_lily(class_name: str) -> int:
    """Re-encode images directly inside the class folder (in place)."""
    class_dir = DATA_DIR / class_name
    files = [p for p in class_dir.iterdir() if is_image(p)]
    backup_images(files, BACKUP_DIR / class_name)
    processed = 0
    for src in files:
        dst = class_dir / (src.stem + ".jpg")
        process_one(src, dst)
        if dst.name != src.name:
            src.unlink(missing_ok=True)
        processed += 1
    return processed


def process_other() -> int:
    """Flatten a random capped sample of the nested ``other`` data."""
    class_dir = DATA_DIR / "other"
    sources = [p for p in class_dir.rglob("*") if is_image(p)]
    if not sources:
        return 0
    backup_images(sources, BACKUP_DIR / "other", relative_to=class_dir)
    sources = random.sample(sources, min(len(sources), OTHER_MAX))

    temp_dir = PROJECT_DIR / "data" / ".other_new"
    if temp_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)
    temp_dir.mkdir(parents=True, exist_ok=True)

    def unique_name(city: str, cat: str) -> str:
        def clean(text: str) -> str:
            return re.sub(r"_+", "_", re.sub(r"[^A-Za-z0-9]+", "_", text)).strip("_")

        return f"{clean(city)}_{clean(cat)}.jpg"

    used = set()
    processed = 0
    for src in sources:
        city = src.parent.parent.name
        cat = src.parent.name
        base = unique_name(city, cat)
        candidate = base
        idx = 1
        while candidate in used:
            candidate = f"{base[:-4]}_{idx}.jpg"
            idx += 1
        used.add(candidate)
        process_one(src, temp_dir / candidate)
        processed += 1

    shutil.rmtree(class_dir, ignore_errors=True)
    os.replace(temp_dir, class_dir)
    return processed


def dir_size_mb(path: Path) -> float:
    total = sum(p.stat().st_size for p in path.rglob("*") if p.is_file())
    return total / (1024 * 1024)


def main() -> None:
    if not DATA_DIR.exists():
        raise FileNotFoundError(f"Data folder not found: {DATA_DIR}")

    print(f"Before: {dir_size_mb(DATA_DIR):.1f} MB")
    print(f"Counts before: {folder_counts()}")

    processed = 0
    processed += process_meko_lily("meko")
    processed += process_meko_lily("lily")
    processed += process_other()

    print(f"Processed {processed} images -> {DATA_DIR}")
    print(f"Counts after: {folder_counts()}")
    print(f"After: {dir_size_mb(DATA_DIR):.1f} MB")
    print(f"Raw backup kept in {BACKUP_DIR} ({dir_size_mb(BACKUP_DIR):.1f} MB, gitignored)")


if __name__ == "__main__":
    main()