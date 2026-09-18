Put labelled photos in the three folders:

- `meko/`: Meko only
- `lily/`: Lily only
- `other/`: any other cat (not Meko or Lily)

The images committed here are **processed** (downscaled to 448 px, EXIF/GPS
stripped, JPEG). Raw originals stay local under `data/originals/` and are
ignored by Git. To re-prepare new photos, run:

```powershell
python prepare_public_data.py
```