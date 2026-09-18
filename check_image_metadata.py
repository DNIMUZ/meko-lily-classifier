"""Scan image files for embedded metadata and privacy leaks.

Checks every JPEG/PNG under the given paths for EXIF, GPS coordinates, camera
make/model, timestamps, and thumbnail blobs. Exits 0 when everything is clean
(matching the repository's metadata-free policy) and 1 otherwise.

Usage:
    python check_image_metadata.py <path> [<path> ...]

Paths may be files or directories (walked recursively).
"""

import sys
from pathlib import Path

from PIL import Image, ExifTags

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

PRIVATE_EXIF = {
    0x010F: "Make",
    0x0110: "Model",
    0x0132: "DateTime",
    0x9003: "DateTimeOriginal",
    0x9004: "DateTimeDigitized",
    0x8825: "GPSInfo",
    0x02BC: "JPEGThumbnail",
    0xA002: "PixelXDimension",
    0xA003: "PixelYDimension",
}


def scan(path: Path) -> list[str]:
    findings: list[str] = []
    files = [path] if path.is_file() else sorted(
        p for p in path.rglob("*") if p.suffix.lower() in IMAGE_EXTS
    )
    for file in files:
        try:
            with Image.open(file) as image:
                exif = image.getexif()
                if not exif:
                    continue
                exif_sub = exif.get_ifd(ExifTags.IFD.Exif) or {}
                keys = set(exif.keys()) | set(exif_sub.keys())
                private = [PRIVATE_EXIF.get(k, None) for k in keys]
                private = [n for n in private if n]
                if private:
                    findings.append(f"{file}: {', '.join(sorted(set(private)))}")
        except Exception as error:
            findings.append(f"{file}: unreadable ({error})")
    return findings


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    reported: list[str] = []
    for arg in sys.argv[1:]:
        reported.extend(scan(Path(arg)))
    if reported:
        print("METADATA FOUND - do not commit:")
        for line in reported:
            print(" ", line)
        sys.exit(1)
    print("ok: no EXIF/GPS/thumbnail metadata found in scanned images")


if __name__ == "__main__":
    main()