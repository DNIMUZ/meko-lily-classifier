"""Flatten extra "other-cat" breed folders into the training set.

Users may drop whole folders of look-alike "other" cat photos under
``data/cats/other/`` (e.g. breed downloads from Kat & Kaggle sets detailed in the
README). This script re-encodes every photo the same way the rest of the
dataset is processed (448 px, JPEG 85, EXIF/GPS stripped), renames them with a
unique ``<Breed>_<n>.jpg`` pattern, backs up the originals under
``data/originals/other/``, and deletes the remaining folder.

The resulting files land in ``data/cats/other/`` which is gitignored, so nothing
personal is ever committed.

Usage:
    python ingest_other_breeds.py
"""

import re
import shutil
from pathlib import Path

from prepare_public_data import process_one

PROJECT_DIR = Path(__file__).parent
DATA_DIR = PROJECT_DIR / "data" / "cats"
OTHER_DIR = DATA_DIR / "other"
BACKUP_DIR = PROJECT_DIR / "data" / "originals" / "other"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"}
BREED_FOLDERS = [p for p in sorted(OTHER_DIR.iterdir()) if p.is_dir()]


def cleaned(name: str) -> str:
    return re.sub(r"_+", "_", re.sub(r"[^A-Za-z0-9]+", "_", name)).strip("_")


def ingest() -> int:
    if not BREED_FOLDERS:
        print("No subfolders under data/cats/other to ingest.")
        return 0
    flat_ids: set[str] = {
        p.stem for p in OTHER_DIR.glob("*.jpg") if p.is_file()
    }
    processed = 0
    for folder in BREED_FOLDERS:
        files = [p for p in folder.iterdir() if p.suffix.lower() in {s.lower() for s in IMAGE_EXTS}]
        if not files:
            print(f"skip {folder.name} (no images)")
            continue
        backup = BACKUP_DIR / folder.name
        backup.mkdir(parents=True, exist_ok=True)
        for src in files:
            dst = backup / src.name
            if not dst.exists():
                shutil.copy2(src, dst)
        base = cleaned(folder.name) or "OtherBreed"
        counter = 0
        for src in files:
            dst = OTHER_DIR / f"{base}_{counter}.jpg"
            while (OTHER_DIR / f"{base}_{counter}.jpg").exists():
                counter += 1
                dst = OTHER_DIR / f"{base}_{counter}.jpg"
            process_one(src, dst)
            flat_ids.add(dst.stem)
            counter += 1
            processed += 1
        shutil.rmtree(folder, ignore_errors=True)
        print(f"ingested {folder.name}: {len(files)} -> data/cats/other/")
    return processed


if __name__ == "__main__":
    print(f"Ingesting {len(BREED_FOLDERS)} breed folder(s) into data/cats/other...")
    total = ingest()
    print(f"Done. {total} images processed into data/cats/other (gitignored).")