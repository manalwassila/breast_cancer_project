import tensorflow as tf
import os

MODEL_PATH = r"c:\Users\manal\breast_cancer_project\models\best_model.keras"

try:
    print(f"Attempting to load model from {MODEL_PATH} with compile=False...")
    model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    print("✅ Model loaded successfully with compile=False!")
    print(model.summary())
except Exception as e:
    print(f"❌ Failed to load model even with compile=False: {e}")
