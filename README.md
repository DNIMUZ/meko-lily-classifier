# Meko or Lily Cat Classifier

A small image-classification project that learns to distinguish two cats, Meko and Lily, from other cats. It trains a pretrained MobileNetV2 model and provides:

- A **Streamlit** app (`app.py`) for photo uploads and a live camera mode, with a cat detector that boxes and labels Meko, Lily, or other cat.
- The live camera mode has a **Flip camera** button to switch the front/rear lens and streams boxed frames to the app in real time.

Read the [project report](PROJECT_REPORT.md) for the requirements, technical design, evaluation plan, risks, and delivery phases.

## 1. Prepare photos

Use several different photos for each cat. Include different poses, lighting, distances, and backgrounds. Avoid putting the same photo, or near-duplicates, in both folders.

```text
data/cats/
├── lily/    # Lily photos only
├── meko/    # Meko photos only
└── other/   # any other cat (not Meko or Lily)
```

Start with at least 30-50 photos per cat. More variety is more valuable than many almost-identical photos. The committed images are processed (downscaled, EXIF stripped); raw photos are kept locally under `data/originals/` and are not committed.

## 2. Install and train

From this folder in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python train.py
```

The first training run downloads MobileNetV2 weights from TensorFlow. The trained model is saved locally under `models/` and is ignored by Git.

## 3. Run the app

```powershell
streamlit run app.py
```

Open the local URL shown by Streamlit. Upload a photo first, then try the live camera mode.

### Live camera mode

Choose **Camera (live)** in the app. The browser captures its own camera and streams small JPEG frames to the app (no WebRTC, works on any hosting including Streamlit Community Cloud). Each frame runs through the cat detector and the classifier on the server CPU, so expect a few frames per second.

- **Flip camera** button switches between the front and rear lenses on phones.
- Detected cats get a box labelled **Meko** or **Lily**; uncertain frames or non-Meko/Lily cats are shown as **other cat**; a frame with no cat says **No cat detected in view**.
- Use **Pause capturing** when done so the stream stops sending frames.

The camera component (`camera_live/`) is a vendored and extended copy of [streamlit-camera-input-live](https://github.com/blackary/streamlit-camera-input-live) (MIT).

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

Replace `<your-username>` with your GitHub username. The project `.gitignore` excludes virtual environments, model files, and photos by default, but still review `git status` carefully before pushing. Never commit passwords, tokens, or private photos accidentally.

## Important limitations

This is a learning project, not proof of identity. If the confidence is low, treat the result as unknown. A model may learn background, collar, or lighting instead of the cat's face, so test with new photos from different places.

Never add private employer or production data to this repository. Cat photos are personal data too, so keep the project private unless you are comfortable publishing them.

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
3. ✅ Live camera mode with cat detection and Meko/Lily/other boxes, including a front/rear flip (`Camera (live)` in `app.py`).
4. ✅ Track precision, recall, and a confusion matrix (now reported by `evaluate.py`).
