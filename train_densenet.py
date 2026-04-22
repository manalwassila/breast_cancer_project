import os
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import DenseNet121
from tensorflow.keras.applications.densenet import preprocess_input
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from tensorflow.keras.regularizers import l2

IMG_SIZE = (224, 224)
BATCH_SIZE = 32

TRAIN_DIR = "data_split/train"
VAL_DIR   = "data_split/val"
TEST_DIR  = "data_split/test"

os.makedirs("models", exist_ok=True)

# ─────────────────────────────────────
# FAST INPUT PIPELINE (IMPORTANT FIX)
# ─────────────────────────────────────
train_ds = tf.keras.utils.image_dataset_from_directory(
    TRAIN_DIR,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="binary"
)

val_ds = tf.keras.utils.image_dataset_from_directory(
    VAL_DIR,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="binary"
)

test_ds = tf.keras.utils.image_dataset_from_directory(
    TEST_DIR,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="binary",
    shuffle=False
)

AUTOTUNE = tf.data.AUTOTUNE
train_ds = train_ds.cache().shuffle(1000).prefetch(AUTOTUNE)
val_ds = val_ds.cache().prefetch(AUTOTUNE)
test_ds = test_ds.prefetch(AUTOTUNE)

# ─────────────────────────────────────
# DATA AUGMENTATION (STRONG + MEDICAL SAFE)
# ─────────────────────────────────────
data_augmentation = tf.keras.Sequential([
    layers.RandomFlip("horizontal_and_vertical"),
    layers.RandomRotation(0.25),
    layers.RandomZoom(0.25),
    layers.RandomContrast(0.2),
])

# ─────────────────────────────────────
# MODEL (TRANSFER LEARNING)
# ─────────────────────────────────────
base_model = DenseNet121(
    weights="imagenet",
    include_top=False,
    input_shape=(224, 224, 3)
)

base_model.trainable = False  # Phase 1

inputs = tf.keras.Input(shape=(224, 224, 3))
x = data_augmentation(inputs)
x = preprocess_input(x)

x = base_model(x, training=False)
x = layers.GlobalAveragePooling2D()(x)
x = layers.BatchNormalization()(x)

x = layers.Dense(
    128,
    activation="relu",
    kernel_regularizer=l2(0.001)
)(x)

x = layers.Dropout(0.5)(x)
outputs = layers.Dense(1, activation="sigmoid")(x)

model = models.Model(inputs, outputs)

# ─────────────────────────────────────
# LOSS (IMPORTANT FOR MEDICAL AI)
# ─────────────────────────────────────
loss_fn = tf.keras.losses.BinaryCrossentropy(label_smoothing=0.1)

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
    loss=loss_fn,
    metrics=["accuracy", tf.keras.metrics.AUC(name="auc")]
)

# ─────────────────────────────────────
# CALLBACKS
# ─────────────────────────────────────
callbacks = [
    ModelCheckpoint(
        "models/best_model.keras",
        monitor="val_auc",
        mode="max",
        save_best_only=True,
        verbose=1
    ),
    EarlyStopping(
        monitor="val_auc",
        patience=3,
        restore_best_weights=True
    ),
    ReduceLROnPlateau(
        monitor="val_loss",
        factor=0.3,
        patience=2,
        min_lr=1e-6
    )
]

# ─────────────────────────────────────
# PHASE 1 - TRAIN HEAD ONLY
# ─────────────────────────────────────
print("\n🚀 Phase 1: training head")

history1 = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=10,
    callbacks=callbacks
)

# ─────────────────────────────────────
# PHASE 2 - FINE TUNING (CONTROLLED)
# ─────────────────────────────────────
print("\n🔥 Phase 2: fine-tuning")

for layer in base_model.layers[-20:]:
    layer.trainable = True

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
    loss=loss_fn,
    metrics=["accuracy", tf.keras.metrics.AUC(name="auc")]
)

history2 = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=10,
    callbacks=callbacks
)

# ─────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────
print("\n📊 Final evaluation")

results = model.evaluate(test_ds)
for name, value in zip(model.metrics_names, results):
    print(f"{name}: {value:.4f}")

model.save("models/final_densenet_medical.keras")

print("\n✅ DONE")