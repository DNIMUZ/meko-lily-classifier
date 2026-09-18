from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps

PROJECT_DIR = Path(__file__).parent
DETECTOR_PATH = PROJECT_DIR / "models" / "detectors" / "yolov8n_coco.onnx"
COCO_CAT_CLASS = 15
DET_INPUT_SIZE = 640
IMAGE_SIZE = (224, 224)
DEFAULT_MIN_CONFIDENCE = 0.60


@dataclass
class CatBox:
    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float


class CatDetector:
    def __init__(self, model_path=DETECTOR_PATH):
        self.net = cv2.dnn.readNetFromONNX(str(model_path))

    def detect(self, frame_bgr, conf_threshold=0.25, iou_threshold=0.45):
        height, width = frame_bgr.shape[:2]
        scale = min(DET_INPUT_SIZE / width, DET_INPUT_SIZE / height)
        new_width = int(round(width * scale))
        new_height = int(round(height * scale))
        resized = cv2.resize(frame_bgr, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
        letterbox = np.full((DET_INPUT_SIZE, DET_INPUT_SIZE, 3), 114, dtype=np.uint8)
        offset_x = (DET_INPUT_SIZE - new_width) // 2
        offset_y = (DET_INPUT_SIZE - new_height) // 2
        letterbox[offset_y : offset_y + new_height, offset_x : offset_x + new_width] = resized
        blob = cv2.dnn.blobFromImage(letterbox, 1.0 / 255.0, (DET_INPUT_SIZE, DET_INPUT_SIZE), swapRB=False, crop=False)
        self.net.setInput(blob)
        output = self.net.forward()[0]
        predictions = output.T
        cat_scores = predictions[:, 4 + COCO_CAT_CLASS]
        candidate_mask = cat_scores >= conf_threshold
        if not candidate_mask.any():
            return []
        candidates = predictions[candidate_mask]
        boxes = []
        scores = []
        for row in candidates:
            cx, cy, box_w, box_h = row[:4]
            score = float(row[4 + COCO_CAT_CLASS])
            x1 = (cx - box_w / 2.0 - offset_x) / scale
            y1 = (cy - box_h / 2.0 - offset_y) / scale
            x2 = (cx + box_w / 2.0 - offset_x) / scale
            y2 = (cy + box_h / 2.0 - offset_y) / scale
            boxes.append([int(x1), int(y1), int(x2 - x1), int(y2 - y1)])
            scores.append(score)
        indices = cv2.dnn.NMSBoxes(boxes, scores, conf_threshold, iou_threshold)
        detections = []
        for index in indices:
            i = int(index)
            x, y, w, h = boxes[i]
            detections.append(CatBox(float(x), float(y), float(x + w), float(y + h), float(scores[i])))
        return detections


def classify_crop(model, crop_bgr, class_names):
    rgb = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(rgb).resize(IMAGE_SIZE)
    pixels = np.asarray(image, dtype=np.uint8)[None, ...]
    probabilities = model.predict(pixels, verbose=0)[0]
    best_index = int(np.argmax(probabilities))
    confidence = float(probabilities[best_index])
    label = "other cat"
    if class_names[best_index] != "other" and confidence >= DEFAULT_MIN_CONFIDENCE:
        label = class_names[best_index].title()
    return label, confidence


def annotate(frame_bgr, model, class_names, detector, conf_threshold=0.25, iou_threshold=0.45):
    height, width = frame_bgr.shape[:2]
    boxes = detector.detect(frame_bgr, conf_threshold, iou_threshold)
    results = []
    for box in boxes:
        margin = 0.08 * max(box.x2 - box.x1, box.y2 - box.y1)
        x1 = int(max(0.0, box.x1 - margin))
        y1 = int(max(0.0, box.y1 - margin))
        x2 = int(min(width, box.x2 + margin))
        y2 = int(min(height, box.y2 + margin))
        crop = frame_bgr[y1:y2, x1:x2]
        if crop.size == 0:
            continue
        label, confidence = classify_crop(model, crop, class_names)
        results.append({"label": label, "confidence": confidence, "box": (x1, y1, x2, y2)})
        if label == "Meko":
            color = (0, 200, 0)
        elif label == "Lily":
            color = (0, 140, 255)
        else:
            color = (160, 160, 160)
        cv2.rectangle(frame_bgr, (x1, y1), (x2, y2), color, 3)
        text = f"{label} ({confidence:.0%})"
        text_scale = 0.7
        text_thickness = 2
        (text_width, text_height), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, text_scale, text_thickness)
        label_y = y1 if y1 - text_height - baseline >= 0 else y2
        cv2.rectangle(frame_bgr, (x1, label_y - text_height - baseline), (x1 + text_width, label_y), color, -1)
        cv2.putText(
            frame_bgr,
            text,
            (x1, label_y - baseline),
            cv2.FONT_HERSHEY_SIMPLEX,
            text_scale,
            (0, 0, 0),
            text_thickness,
        )
    return frame_bgr, results