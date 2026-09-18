from pathlib import Path
import json

import numpy as np
import streamlit as st
from PIL import Image, ImageOps
from tensorflow import keras

PROJECT_DIR = Path(__file__).parent
MODEL_PATH = PROJECT_DIR / "models" / "meko_lily.keras"
CLASS_NAMES_PATH = PROJECT_DIR / "models" / "class_names.json"
IMAGE_SIZE = (224, 224)

st.set_page_config(page_title="Meko or Lily?", page_icon="🐱")
st.title("Meko or Lily?")
st.caption("Upload a cat photo, or use the camera input when a camera is available.")

if not MODEL_PATH.exists() or not CLASS_NAMES_PATH.exists():
    st.warning("The model has not been trained yet. Add photos to data/cats/meko and data/cats/lily, then run: python train.py")
    st.stop()

@st.cache_resource
def load_assets():
    model = keras.models.load_model(MODEL_PATH)
    class_names = json.loads(CLASS_NAMES_PATH.read_text(encoding="utf-8"))
    return model, class_names

model, class_names = load_assets()
source = st.radio("Choose an image source", ["Upload photo", "Camera"], horizontal=True)
photo = st.file_uploader("Choose a cat image", type=["jpg", "jpeg", "png"])
if source == "Camera":
    camera_photo = st.camera_input("Take a photo")
    photo = camera_photo or photo

if photo is not None:
    image = Image.open(photo).convert("RGB")
    image = ImageOps.exif_transpose(image)
    st.image(image, caption="Input photo", use_container_width=True)
    resized = image.resize(IMAGE_SIZE)
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
        st.info("The model is unsure. Add more varied, well-labelled photos and retrain.")
