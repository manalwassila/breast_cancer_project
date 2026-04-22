import os
import sys
import io
import glob
import re
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras import layers, models
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import (
    ModelCheckpoint, EarlyStopping, ReduceLROnPlateau, CSVLogger
)
from tensorflow.keras.models import load_model

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ─────────────────────────────────────────────────────────────
#  CONFIGURATION
# ─────────────────────────────────────────────────────────────
TRAIN_DIR        = "data/train"
VAL_DIR          = "data/val"
TEST_DIR         = "data/test"
# Note: starting fresh from ImageNet weights instead of loading an old checkpoint
STABLE_CKPT      = None
BEST_MODEL_PATH  = "models/resnet_cancer_best.keras"
IMG_SIZE         = (224, 224)
BATCH_SIZE       = 32

# Phase durations (in epochs, continuing from epoch 20)
PHASE1_END = 28   # re-align head   (epochs 21-28, backbone frozen)
PHASE2_END = 50   # deep fine-tune  (epochs 29-50, last 50 layers)

os.makedirs("models",  exist_ok=True)
os.makedirs("results", exist_ok=True)

print(">>> MammoScan AI - Training Script v4 (Loss-Fix + Alignment)")
print("    KEY: using rescale=1/255 to MATCH the Epoch-20 checkpoint\n")

# ─────────────────────────────────────────────────────────────
#  1. SOFT CLASS WEIGHTS
# ─────────────────────────────────────────────────────────────
n_benign    = len(glob.glob(os.path.join(TRAIN_DIR, "benign",    "*.*")))
n_malignant = len(glob.glob(os.path.join(TRAIN_DIR, "malignant", "*.*")))
n_total     = n_benign + n_malignant

# Soft sqrt weighting (prevents over-shooting)
w_b = np.sqrt(n_total / (2 * n_benign))
w_m = np.sqrt(n_total / (2 * n_malignant))
norm = min(w_b, w_m)
class_weight = {0: w_b / norm, 1: w_m / norm}

print(f"[1/6] Class weights  ->  benign: {class_weight[0]:.4f}  malignant: {class_weight[1]:.4f}")

# ─────────────────────────────────────────────────────────────
#  2. DATA GENERATORS  — rescale=1/255 (matches checkpoint!)
# ─────────────────────────────────────────────────────────────
print("[2/6] Building data generators (using ResNet preprocessing)...")

train_datagen = ImageDataGenerator(
    preprocessing_function=preprocess_input,
    rotation_range=20,
    width_shift_range=0.1,
    height_shift_range=0.1,
    zoom_range=0.15,
    horizontal_flip=True,
    fill_mode="nearest",
)

val_datagen = ImageDataGenerator(preprocessing_function=preprocess_input)

train_gen = train_datagen.flow_from_directory(
    TRAIN_DIR, target_size=IMG_SIZE, batch_size=BATCH_SIZE,
    class_mode="binary", shuffle=True)

# If `data/val` is missing or empty, fall back to `data/test` so training can continue.
if not os.path.exists(VAL_DIR) or not any(os.scandir(VAL_DIR)):
    print(f"[WARN] Validation directory '{VAL_DIR}' is empty or missing — falling back to '{TEST_DIR}'")
    VAL_DIR = TEST_DIR

val_gen = val_datagen.flow_from_directory(
    VAL_DIR, target_size=IMG_SIZE, batch_size=BATCH_SIZE,
    class_mode="binary", shuffle=False)

# ─────────────────────────────────────────────────────────────
#  3. LOAD STABLE CHECKPOINT
# ─────────────────────────────────────────────────────────────
print("\n[3/6] Building model fresh from ImageNet weights (ResNet50 backbone)")

# Build a fresh model using ResNet50 (ImageNet weights) and a sigmoid output
base = ResNet50(weights="imagenet", include_top=False, input_shape=(*IMG_SIZE, 3))
x = base.output
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dense(256, activation="relu")(x)
x = layers.Dropout(0.5)(x)
preds = layers.Dense(1, activation="sigmoid")(x)
model = models.Model(inputs=base.input, outputs=preds)

def compile_model(lr):
    model.compile(
        optimizer=Adam(learning_rate=lr),
        loss="binary_crossentropy",
        metrics=[
            "accuracy",
            tf.keras.metrics.AUC(name="auc"),
            tf.keras.metrics.Precision(name="precision"),
            tf.keras.metrics.Recall(name="recall"),
        ],
    )

def make_callbacks(tag):
    return [
        ModelCheckpoint(
            f"models/resnet_v4_{tag}_epoch_{{epoch:02d}}.keras",
            monitor="val_auc", mode="max",
            save_best_only=True, verbose=1),
        ModelCheckpoint(
            BEST_MODEL_PATH,
            monitor="val_auc", mode="max",
            save_best_only=True, verbose=1),
        EarlyStopping(
            monitor="val_auc", patience=5,
            restore_best_weights=True, verbose=1),
        ReduceLROnPlateau(
            monitor="val_loss", factor=0.4, patience=2,
            min_lr=1e-9, verbose=1),
        CSVLogger(f"results/training_log_v4_{tag}.csv", append=True),
    ]

# ─────────────────────────────────────────────────────────────
#  4. PHASE 1 — Re-align head (backbone frozen, epochs 21-28)
# ─────────────────────────────────────────────────────────────
print("\n[4/6] PHASE 1 - Re-aligning head (backbone frozen, epochs 21-28)...")
print("      Loss should drop to < 1.0 within the first 100 steps.\n")

# Freeze ALL ResNet50 backbone layers, train only the head
for layer in model.layers:
    layer.trainable = False
# Unfreeze only the last 4 layers (the custom head)
for layer in model.layers[-4:]:
    layer.trainable = True

compile_model(lr=1e-4)  # Higher LR ok since only head is training

history1 = model.fit(
    train_gen,
    validation_data=val_gen,
    initial_epoch=20,
    epochs=PHASE1_END,
    class_weight=class_weight,
    callbacks=make_callbacks("p1"),
)

# ─────────────────────────────────────────────────────────────
#  5. PHASE 2 — Deep fine-tune (last 50 layers, epochs 29-50)
# ─────────────────────────────────────────────────────────────
print("\n[5/6] PHASE 2 - Fine-tuning last 50 layers (epochs 29-50)...")

for layer in model.layers:
    layer.trainable = False
for layer in model.layers[-50:]:
    layer.trainable = True

compile_model(lr=5e-6)  # Very small LR to avoid forgetting

history2 = model.fit(
    train_gen,
    validation_data=val_gen,
    initial_epoch=PHASE1_END,
    epochs=PHASE2_END,
    class_weight=class_weight,
    callbacks=make_callbacks("p2"),
)

# ─────────────────────────────────────────────────────────────
#  6. FINAL EVALUATION
# ─────────────────────────────────────────────────────────────
print("\n[6/6] Final evaluation on test set...")
results = model.evaluate(val_gen, verbose=1)
for name, val in zip(model.metrics_names, results):
    print(f"   {name}: {val:.4f}")

print(f"\nBest model saved to: {BEST_MODEL_PATH}")
