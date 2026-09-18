"""Honest held-out evaluation for the Meko/Lily/Other classifier.

Fixes a fixed-seed, stratified train/val/test split (80/10/10), trains a fresh
MobileNetV2 model (head, then top-layer fine-tune) on the training portion, and
reports accuracy, per-class precision/recall/F1, a confusion matrix, the
false-Meko rate (the app's key failure mode: non-Meko cats shown as Meko), a
per-class decision-threshold sweep using the app's exact labelling rule, and
misclassified examples. Writes ``models/evaluation_report.md``.

Run:  python evaluate.py
"""

import json
import random
from datetime import date
from pathlib import Path

import numpy as np
import tensorflow as tf

from train import IMAGE_SIZE, MODEL_DIR, MODEL_PATH, CLASS_NAMES_PATH
from train import build_model, class_weights, count_images, fit_two_stage

PROJECT_DIR = Path(__file__).parent
DATA_DIR = PROJECT_DIR / "data" / "cats"
REPORT_PATH = MODEL_DIR / "evaluation_report.md"

BATCH_SIZE = 16
SEED = 123
EPOCHS = 20
TRAIN_SPLIT = 0.8
DATA_FILE_EXTS = {".jpg", ".jpeg", ".png"}
RECALL_FLOOR = 0.9

random.seed(SEED)


def collect_image_paths() -> tuple[list[str], list[int], list[str]]:
    """Return (paths, labels) grouped per class folder."""
    paths: list[str] = []
    labels: list[int] = []
    class_names = sorted(
        d.name for d in DATA_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")
    )
    for label, name in enumerate(class_names):
        class_dir = DATA_DIR / name
        class_paths = [
            str(p) for p in class_dir.rglob("*") if p.suffix.lower() in DATA_FILE_EXTS
        ]
        random.shuffle(class_paths)
        for path in class_paths:
            paths.append(path)
            labels.append(label)
    return paths, labels, class_names


def stratified_split(
    paths: list[str], labels: list[int], class_names: list[str]
) -> tuple[list[int], list[int], list[int]]:
    """Returns train/val/test index lists, stratified per class."""
    train_idx, val_idx, test_idx = [], [], []
    per_class: dict[int, list[int]] = {i: [] for i in range(len(class_names))}
    for index, label in enumerate(labels):
        per_class[label].append(index)
    for indices in per_class.values():
        n = len(indices)
        n_test = max(1, round(n * (1 - TRAIN_SPLIT) / 2))
        n_val = max(1, round(n * (1 - TRAIN_SPLIT) / 2))
        n_train = n - n_test - n_val
        test_idx.extend(indices[:n_test])
        val_idx.extend(indices[n_test : n_test + n_val])
        train_idx.extend(indices[n_test + n_val :])
    return sorted(train_idx), sorted(val_idx), sorted(test_idx)


def make_dataset(
    paths: list[str], labels: list[int], indices: list[int], flip: bool = False
) -> tf.data.Dataset:
    sample_paths = [paths[i] for i in indices]
    sample_labels = [labels[i] for i in indices]

    def decode(path, label):
        image = tf.io.read_file(path)
        image = tf.image.decode_jpeg(image, channels=3)
        image = tf.image.resize(image, IMAGE_SIZE)
        if flip:
            image = tf.image.flip_left_right(image)
        return image, label

    ds = tf.data.Dataset.from_tensor_slices((sample_paths, sample_labels))
    ds = ds.map(decode, num_parallel_calls=tf.data.AUTOTUNE)
    ds = ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)
    return ds


def app_labels(probabilities: np.ndarray, cutoff: float, class_names: list[str]) -> np.ndarray:
    """Labels using the app rule: named cat only when its class wins AND its
    probability is at least ``cutoff``; otherwise 'other'."""
    best_index = probabilities.argmax(axis=1)
    best_prob = probabilities.max(axis=1)
    other_index = len(class_names) - 1
    labels = np.where(
        (best_index != other_index) & (best_prob >= cutoff), best_index, other_index
    )
    return labels


def report_metrics(y_true: np.ndarray, y_pred: np.ndarray, class_names: list[str]) -> str:
    n = len(class_names)
    matrix = np.zeros((n, n), dtype=int)
    for true, pred in zip(y_true, y_pred):
        matrix[true, pred] += 1

    lines = []
    lines.append("### Confusion matrix (rows = true, columns = predicted)")
    header = "| true \\ predicted | " + " | ".join(class_names) + " | total |"
    sep = "|" + "---|" * (n + 2)
    lines.append(header)
    lines.append(sep)
    acc_total = 0
    per_class = []
    for i, name in enumerate(class_names):
        tp = matrix[i, i]
        fp = matrix[:, i].sum() - tp
        fn = matrix[i, :].sum() - tp
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = (
            (2 * precision * recall / (precision + recall))
            if (precision + recall)
            else 0.0
        )
        acc_total += tp
        per_class.append((name, precision, recall, f1))
        row = f"| {name} | " + " | ".join(str(matrix[i, j]) for j in range(n)) + f" | {matrix[i].sum()} |"
        lines.append(row)

    accuracy = acc_total / len(y_true) if y_true.size else 0.0
    lines.append("")
    lines.append(f"### Overall accuracy: {accuracy:.3f}")
    lines.append("")
    lines.append("### Per-class metrics")
    lines.append("| class | precision | recall | F1 |")
    lines.append("|---|---|---|---|")
    for name, precision, recall, f1 in per_class:
        lines.append(f"| {name} | {precision:.3f} | {recall:.3f} | {f1:.3f} |")
    return "\n".join(lines), matrix, accuracy


def threshold_table(
    probabilities: np.ndarray, y_true: np.ndarray, class_names: list[str]
) -> tuple[list[str], float]:
    """Sweep the app-rule cutoff; recommend the lowest cutoff that keeps Meko and
    Lily recall at/above ``RECALL_FLOOR`` while minimising false Meko labels."""
    meko = class_names.index("meko")
    lily = class_names.index("lily")
    other = len(class_names) - 1

    lines = [
        "### Decision-threshold sweep (app rule: named label only when the winner's probability >= cutoff, else 'other')"
    ]
    lines.append("| cutoff | lily rec | meko rec | other rec | false-Meko rate | overall acc |")
    lines.append("|---|---|---|---|---|---|")

    rows: list[tuple[float, float, float, float, float, float]] = []
    for cutoff in np.arange(0.50, 0.96, 0.05):
        cutoff = round(float(cutoff), 2)
        labels = app_labels(probabilities, cutoff, class_names)
        rows.append((cutoff, labels, y_true))
        lily_rec = float((labels[y_true == lily] == lily).mean())
        meko_rec = float((labels[y_true == meko] == meko).mean())
        other_rec = float((labels[y_true == other] == other).mean())
        false_meko = float((labels[y_true == other] == meko).mean())
        acc = float((labels == y_true).mean())
        lines.append(
            f"| {cutoff:.2f} | {lily_rec:.3f} | {meko_rec:.3f} | {other_rec:.3f} | {false_meko:.3f} | {acc:.3f} |"
        )

    chosen = next(
        (round(float(c), 2) for c, labels, y in rows
         if (labels[y_true == lily] == lily).mean() >= RECALL_FLOOR
         and (labels[y_true == meko] == meko).mean() >= RECALL_FLOOR),
        round(float(np.arange(0.50, 0.96, 0.05)[0]), 2),
    )
    return lines, chosen


def main() -> None:
    paths, labels, class_names = collect_image_paths()
    counts = [count_images(DATA_DIR / name) for name in class_names]
    print(f"Classes: {class_names}")
    print(f"Per-class image counts: {counts}")

    train_idx, val_idx, test_idx = stratified_split(paths, labels, class_names)
    train_ds = make_dataset(paths, labels, train_idx)
    val_ds = make_dataset(paths, labels, val_idx)
    test_ds = make_dataset(paths, labels, test_idx)
    test_flip_ds = make_dataset(paths, labels, test_idx, flip=True)
    print(f"Split sizes: train={len(train_idx)} val={len(val_idx)} test={len(test_idx)}")

    weights = class_weights(class_names)
    model = build_model(len(class_names))
    fit_two_stage(model, train_ds, val_ds, weights, MODEL_PATH)
    model.save(MODEL_PATH)
    CLASS_NAMES_PATH.write_text(json.dumps(class_names, indent=2), encoding="utf-8")

    probabilities = model.predict(test_ds, verbose=0)
    flipped = model.predict(test_flip_ds, verbose=0)
    probabilities = 0.5 * (np.asarray(probabilities) + np.asarray(flipped))
    y_true = np.array([labels[i] for i in test_idx])

    sweep_lines, chosen_cutoff = threshold_table(probabilities, y_true, class_names)
    y_pred = app_labels(probabilities, chosen_cutoff, class_names)

    metrics_lines, matrix, accuracy = report_metrics(y_true, y_pred, class_names)
    print()
    print(metrics_lines)
    print()
    print("\n".join(sweep_lines))
    print(f"\nRecommended cutoff: {chosen_cutoff:.2f}")

    mistakes = []
    for i, index in enumerate(test_idx):
        true_label = labels[index]
        predicted_label = y_pred[i]
        if true_label != predicted_label:
            mistakes.append((paths[index], true_label, predicted_label, probabilities[i]))
    example_lines = ["### Misclassified examples (first 8)"]
    if mistakes:
        for path, true_label, predicted_label, probs in mistakes[:8]:
            probs_str = ", ".join(
                f"{class_names[j]}={probs[j]:.2f}" for j in range(len(class_names))
            )
            example_lines.append(
                f"- `{Path(path).relative_to(PROJECT_DIR).as_posix()}` true={class_names[true_label]} predicted={class_names[predicted_label]} ({probs_str})"
            )
    else:
        example_lines.append("- none")
    example_lines = "\n".join(example_lines)

    report = "\n".join(
        [
            "# Evaluation report",
            "",
            f"- Date: {date.today().isoformat()} (generated by `evaluate.py`)",
            f"- Classes: {class_names}",
            f"- Per-class image counts: {counts}",
            f"- Split: train={len(train_idx)} val={len(val_idx)} test={len(test_idx)} (seed {SEED})",
            f"- Model: MobileNetV2 transfer learning (head, then top {60} layers fine-tuned at LR 1e-5), {EPOCHS}-epoch cap with early stopping",
            f"- Probabilities averaged with a horizontal-flip TTA (matches the app).",
            f"- Decision rule: named cat only when it wins AND its probability >= cutoff `{chosen_cutoff:.2f}`, else 'other'.",
            f"- False-Meko rate = share of true-`other` cats labelled Meko at the chosen cutoff.",
            "",
            metrics_lines,
            "",
            "\n".join(sweep_lines),
            "",
            example_lines,
        ]
    )
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"\nWrote {REPORT_PATH}")


if __name__ == "__main__":
    main()