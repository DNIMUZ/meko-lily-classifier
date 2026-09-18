from io import BytesIO
from pathlib import Path
import json

import numpy as np
import streamlit as st
from PIL import Image, ImageOps
from tensorflow import keras

from camera_live import camera_live
from vision import PROJECT_DIR, CatDetector, IMAGE_SIZE, annotate

MODEL_PATH = PROJECT_DIR / "models" / "meko_lily.keras"
CLASS_NAMES_PATH = PROJECT_DIR / "models" / "class_names.json"

st.set_page_config(page_title="Meko or Lily?", page_icon="🐱")
st.title("Meko or Lily?")
st.caption("Upload a photo or stream the camera live. Cats are boxed as Meko, Lily, or other cat.")

if not MODEL_PATH.exists() or not CLASS_NAMES_PATH.exists():
    st.warning("The model has not been trained yet. Add photos to data/cats/meko and data/cats/lily, then run: python train.py")
    st.stop()


@st.cache_resource
def load_assets():
    model = keras.models.load_model(MODEL_PATH)
    class_names = json.loads(CLASS_NAMES_PATH.read_text(encoding="utf-8"))
    detector = CatDetector()
    return model, class_names, detector


model, class_names, detector = load_assets()


def to_bgr(image_rgb: Image.Image) -> np.ndarray:
    return np.asarray(image_rgb)[:, :, ::-1].copy()


def analyze(image_rgb: Image.Image):
    annotated, results = annotate(to_bgr(image_rgb), model, class_names, detector)
    return annotated[:, :, ::-1].copy(), results


def render_results(annotated_rgb, results, caption: str):
    st.image(annotated_rgb, caption=caption, use_container_width=True)
    known = [result for result in results if result["label"] != "other cat"]
    if known:
        summary = ", ".join(f"{result['label']} ({result['confidence']:.0%})" for result in results)
        st.subheader(f"Found {len(results)} cat{'s' if len(results) != 1 else ''}: {summary}")
    else:
        st.subheader("Neither Meko nor Lily — looks like another cat.")
    for result in results:
        st.caption(f"Boxed as {result['label']} at {result['confidence']:.1%} confidence")


def render_full_image(image_rgb: Image.Image):
    st.image(image_rgb, caption="Input photo", use_container_width=True)
    resized = image_rgb.resize(IMAGE_SIZE)
    pixels = np.asarray(resized, dtype=np.uint8)[None, ...]
    probabilities = model.predict(pixels, verbose=0)[0]
    best_index = int(np.argmax(probabilities))
    best_name = class_names[best_index]
    confidence = float(probabilities[best_index])
    if best_name == "other":
        st.subheader("Neither Meko nor Lily — looks like another cat.")
    else:
        st.subheader(f"This looks like {best_name.title()}")
    st.metric("Confidence", f"{confidence:.1%}")
    st.bar_chart({name.title(): float(probabilities[index]) for index, name in enumerate(class_names)})
    if confidence < 0.70:
        st.info("No cat was detected by the detector, so the full image was classified. The model is unsure — add more varied, well-labelled photos and retrain.")


source = st.radio("Choose an image source", ["Upload photo", "Camera (live)"], horizontal=True)

if source == "Camera (live)":
    st.info("The camera streams live frames to the app and boxes cats in real time. Use Flip camera to switch the front/rear lens.")
    frame = camera_live(debounce_ms=300, key="meko-lily-cam")
    if frame is not None:
        image = Image.open(frame).convert("RGB")
        image = ImageOps.exif_transpose(image)
        annotated_rgb, results = analyze(image)
        if results:
            render_results(annotated_rgb, results, "Live camera")
        else:
            st.image(annotated_rgb, caption="Live camera", use_container_width=True)
            st.subheader("No cat detected in view.")
else:
    photo = st.file_uploader("Choose a cat image", type=["jpg", "jpeg", "png"])
    if photo is not None:
        image = Image.open(photo).convert("RGB")
        image = ImageOps.exif_transpose(image)
        annotated_rgb, results = analyze(image)
        if results:
            render_results(annotated_rgb, results, "Detected cats")
        else:
            render_full_image(image)