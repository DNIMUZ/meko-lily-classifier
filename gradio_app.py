import json

import gradio as gr
import numpy as np
from tensorflow import keras

from vision import PROJECT_DIR, CatDetector, annotate

MODEL_PATH = PROJECT_DIR / "models" / "meko_lily.keras"
CLASS_NAMES_PATH = PROJECT_DIR / "models" / "class_names.json"

model = keras.models.load_model(MODEL_PATH)
class_names = json.loads(CLASS_NAMES_PATH.read_text(encoding="utf-8"))
detector = CatDetector()


def process_frame(frame_rgb):
    if frame_rgb is None:
        return None
    frame_rgb = np.asarray(frame_rgb)
    if frame_rgb.ndim != 3 or frame_rgb.shape[-1] != 3:
        return frame_rgb
    frame_bgr = frame_rgb[:, :, ::-1].copy()
    annotated, _ = annotate(frame_bgr, model, class_names, detector)
    return annotated[:, :, ::-1]


def build_demo():
    with gr.Blocks(title="Meko or Lily? Live") as demo:
        gr.Markdown("# Meko or Lily? Live")
        gr.Markdown(
            "Point the webcam at a cat, or upload a photo. Cats are boxed and labelled "
            "**Meko** or **Lily**; anything uncertain or non-Meko/Lily is shown as **other cat**."
        )
        with gr.Tab("Live webcam"):
            live_input = gr.Image(sources=["webcam"], streaming=True, type="numpy", mirror_webcam=False)
            live_output = gr.Image(type="numpy", label="Meko, Lily, or other cat")
            live_input.stream(process_frame, inputs=live_input, outputs=live_output, stream_every=0.3, show_progress="hidden")
        with gr.Tab("Upload photo"):
            upload_input = gr.Image(sources=["upload"], type="numpy")
            upload_output = gr.Image(type="numpy", label="Meko, Lily, or other cat")
            upload_input.change(process_frame, inputs=upload_input, outputs=upload_output)
    return demo


if __name__ == "__main__":
    build_demo().launch()