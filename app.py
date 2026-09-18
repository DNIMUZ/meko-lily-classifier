from pathlib import Path
import json

import av
import numpy as np
import streamlit as st
from PIL import Image, ImageOps
from streamlit_webrtc import VideoProcessorBase, WebRtcMode, webrtc_streamer
from tensorflow import keras

from vision import PROJECT_DIR, CatDetector, IMAGE_SIZE, annotate

MODEL_PATH = PROJECT_DIR / "models" / "meko_lily.keras"
CLASS_NAMES_PATH = PROJECT_DIR / "models" / "class_names.json"

st.set_page_config(page_title="Meko or Lily?", page_icon="🐱")
st.title("Meko or Lily?")
st.caption("Upload a photo, take a snapshot, or stream live video. Cats are boxed as Meko, Lily, or other cat.")

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


class CatVideoProcessor(VideoProcessorBase):
    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        image_bgr = frame.to_ndarray(format="bgr24")
        annotated, _ = annotate(image_bgr, model, class_names, detector)
        return av.VideoFrame.from_ndarray(annotated, format="bgr24")


source = st.radio("Choose an image source", ["Upload photo", "Snapshot camera", "Live video"], horizontal=True)

if source == "Live video":
    st.info("Press Start to stream the camera. Live frames are boxed as Meko, Lily, or other cat.")
    webrtc_streamer(
        key="meko-lily-live",
        mode=WebRtcMode.SENDRECV,
        video_processor_factory=CatVideoProcessor,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )
else:
    photo = st.file_uploader("Choose a cat image", type=["jpg", "jpeg", "png"])
    if source == "Snapshot camera":
        camera_photo = st.camera_input("Take a photo")
        photo = camera_photo or photo

    if photo is not None:
        image = Image.open(photo).convert("RGB")
        image = ImageOps.exif_transpose(image)
        frame_bgr = np.asarray(image)[:, :, ::-1].copy()
        annotated, results = annotate(frame_bgr, model, class_names, detector)
        if results:
            st.image(annotated[:, :, ::-1], caption="Detected cats", use_container_width=True)
            known = [result for result in results if result["label"] != "other cat"]
            if known:
                summary = ", ".join(f"{result['label']} ({result['confidence']:.0%})" for result in results)
                st.subheader(f"Found {len(results)} cat{'s' if len(results) != 1 else ''}: {summary}")
            else:
                st.subheader("Neither Meko nor Lily — looks like another cat.")
            for result in results:
                st.caption(f"Boxed as {result['label']} at {result['confidence']:.1%} confidence")
        else:
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
                st.info("No cat was detected by the detector, so the full image was classified. The model is unsure — add more varied, well-labelled photos and retrain.")
