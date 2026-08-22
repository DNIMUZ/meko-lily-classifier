from pathlib import Path
import json

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

PROJECT_DIR = Path(__file__).parent
DATA_DIR = PROJECT_DIR / "data" / "cats"
MODEL_DIR = PROJECT_DIR / "models"
MODEL_PATH = MODEL_DIR / "meko_lily.keras"
CLASS_NAMES_PATH = MODEL_DIR / "class_names.json"
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 16
SEED = 42


def build_model(class_count: int) -> keras.Model:
    augmentation = keras.Sequential(
        [
            layers.RandomFlip("horizontal"),
            layers.RandomRotation(0.08),
            layers.RandomZoom(0.1),
        ],
        name="augmentation",
    )
    base_model = keras.applications.MobileNetV2(
        input_shape=(*IMAGE_SIZE, 3),
        include_top=False,
        weights="imagenet",
    )
    base_model.trainable = False

    inputs = keras.Input(shape=(*IMAGE_SIZE, 3))
    x = augmentation(inputs)
    x = keras.applications.mobilenet_v2.preprocess_input(x)
    x = base_model(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.2)(x)
    outputs = layers.Dense(class_count, activation="softmax")(x)
    model = keras.Model(inputs, outputs)
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def main() -> None:
    if not DATA_DIR.exists():
        raise FileNotFoundError(f"Training folder not found: {DATA_DIR}")

    train_ds = tf.keras.utils.image_dataset_from_directory(
        DATA_DIR,
        validation_split=0.2,
        subset="training",
        seed=SEED,
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
    )
    validation_ds = tf.keras.utils.image_dataset_from_directory(
        DATA_DIR,
        validation_split=0.2,
        subset="validation",
        seed=SEED,
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
    )

    class_names = train_ds.class_names
    if len(class_names) != 2:
        raise ValueError(f"Expected exactly two folders, found: {class_names}")

    autotune = tf.data.AUTOTUNE
    train_ds = train_ds.prefetch(autotune)
    validation_ds = validation_ds.prefetch(autotune)
    model = build_model(len(class_names))
    callbacks = [
        keras.callbacks.EarlyStopping(patience=4, restore_best_weights=True),
        keras.callbacks.ModelCheckpoint(MODEL_PATH, save_best_only=True),
    ]
    model.fit(train_ds, validation_data=validation_ds, epochs=15, callbacks=callbacks)
    model.save(MODEL_PATH)
    CLASS_NAMES_PATH.write_text(json.dumps(class_names, indent=2), encoding="utf-8")
    print(f"Saved model to {MODEL_PATH}")
    print(f"Class order: {class_names}")


if __name__ == "__main__":
    main()
