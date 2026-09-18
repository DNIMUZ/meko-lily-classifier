# Meko or Lily Cat Classifier

A small image-classification project that learns to distinguish two cats, Meko and Lily, from other cats. It trains a pretrained MobileNetV2 model and provides:

- A **Streamlit** app (`app.py`) for photo uploads and snapshot camera, with a cat detector that boxes and labels Meko, Lily, or other cat.
- A **live webcam** mode inside the same Streamlit app (WebRTC) that streams frames and updates the boxes in real time.

Read the [project report](PROJECT_REPORT.md) for the requirements, technical design, evaluation plan, risks, and delivery phases.

## 1. Prepare photos (kept private)

Training photos live only in your **local, gitignored** `data/cats/` folder — they are
never committed. Use several different photos for each cat: different poses,
lighting, distances, and backgrounds. Avoid putting the same photo, or
near-duplicates, in both folders.

```text
data/cats/
├── lily/    # Lily photos only
├── meko/    # Meko photos only
└── other/   # any other cat (not Meko or Lily)
```

Start with at least 30-50 photos per cat. More variety is more valuable than many
almost-identical photos. Everything in `data/cats/` is processed (downscaled to 448 px,
EXIF/GPS stripped, JPEG) and kept out of Git; raw photos stay under `data/originals/`.

To know which cat is which, see the two sample images committed here:
`samples/meko.jpg` and `samples/lily.jpg`.

Extra "other cat" photos dropped as folders under `data/cats/other/` (for example the
breed downloads listed in [Dataset credits](#dataset-credits-and-privacy)) can be
flattened into the training set with:

```powershell
python ingest_other_breeds.py
```

## 2. Install and train

From this folder in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python train.py
```

The first training run downloads MobileNetV2 weights from TensorFlow. Run
`python evaluate.py` for the standard held-out evaluation (per-class metrics,
false-Meko rate, threshold sweep) which writes `models/evaluation_report.md`.
The trained model is saved under `models/` (only the committed `.keras` file is
kept in Git).

## 3. Run the app

```powershell
streamlit run app.py
```

Open the local URL shown by Streamlit. Upload a photo now. When a camera is available, choose `Snapshot camera` and allow browser camera access.

### Live video (WebRTC)

The Streamlit app has a **Live video** source built on `streamlit-webrtc`. Select it, press **Start**, approve camera access, and the feed streams directly to the app. Frames are processed on the server CPU, so expect a few frames per second. Detected cats get a box labelled **Meko** or **Lily**; uncertain frames or non-Meko/Lily cats are shown as **other cat**.

## 4. Push to GitHub

Create a new GitHub repository, preferably private while it contains personal cat photos. Check the files before committing, then run these commands from this folder:

```powershell
git init
git add .
git status
git commit -m "Add Meko and Lily cat classifier"
git branch -M main
git remote add origin https://github.com/<your-username>/meko-lily-classifier.git
git push -u origin main
```

Replace `<your-username>` with your GitHub username. The project `.gitignore`
excludes virtual environments, `data/cats/`, and `data/originals/`, but always
review `git status` carefully before pushing. Before adding any image, run the
metadata guard:

```powershell
python check_image_metadata.py samples
```

Never commit passwords, tokens, or private photos accidentally.

## Important limitations

This is a learning project, not proof of identity. If the confidence is low, treat the result as unknown. A model may learn background, collar, or lighting instead of the cat's face, so test with new photos from different places.

Never add private employer or production data to this repository. Cat photos are personal data too, so keep the project private unless you are comfortable publishing them.

## Dataset credits and privacy

The cats Meko and Lily are the owner's own pets. Their photos are **private** and
are **not** published in this repository (only the two sample images in
`samples/` are included so readers know which cat is which). All training data in
`data/cats/` is gitignored.

The `other` class — random cats that are neither Meko nor Lily — was built from
publicly available photos, credited below. To reproduce or extend the `other`
class, download from these sources, drop the images (as folders or files) into
`data/cats/other/`, and run `python ingest_other_breeds.py`.

- **Phoenix Animal Rescue cats** — bulk of the `other` class:
  https://data.mendeley.com/datasets/ng6tv57j5c/1
- **Sample cat images for model testing** (city-labelled cat photos):
  https://www.kaggle.com/datasets/jackmustonen/sample-cat-images-for-model-testing
- **Cat breeds** — breed photos (for example Bengal, Persian, Tabby, Local,
  Mixed Breed) used as *look-alike* hard negatives that resemble Meko/Lily but
  are neither: https://www.kaggle.com/datasets/nikolasgegenava/cat-breeds

Per-image attribution remains with the original sources; this project only uses
a small processed subset locally.

## Useful references

- [TensorFlow image-classification tutorial source](https://github.com/tensorflow/docs/blob/master/site/en/tutorials/images/classification.ipynb)
- [Keras transfer-learning guide source](https://github.com/keras-team/keras-io/blob/master/guides/transfer_learning.py)
- [Streamlit image-classifier example](https://github.com/streamlit/example-app-image-classifier)
- [TensorFlow image classification tutorial](https://www.tensorflow.org/tutorials/images/classification)
- [Keras transfer learning guide](https://keras.io/guides/transfer_learning/)
- [Streamlit image display documentation](https://docs.streamlit.io/develop/api-reference/media/st.image)
- [Streamlit camera input documentation](https://docs.streamlit.io/develop/api-reference/widgets/st.camera_input)

## Next improvements

1. ✅ Hold out photos taken on different days for a more honest test set (see `evaluate.py`).
2. ✅ Add a third `other` class for random cats so the model can say "neither Meko nor Lily" (`data/cats/other`).
3. ✅ Live webcam mode with cat detection and Meko/Lily/other boxes (`Live video` in `app.py`, WebRTC).
4. ✅ Track precision, recall, and a confusion matrix (now reported by `evaluate.py`).
5. ✅ Two-stage fine-tune (unfrozen MobileNetV2 top layers) + look-alike hard negatives in `other` to kill false-Meko labels; false-Meko rate now reported by `evaluate.py`.
6. ✅ Privacy hardening: `data/cats/` no longer committed; `check_image_metadata.py` guards EXIF/GPS leaks.
