import tensorflow as tf
import os

MODEL_PATH = r"c:\Users\manal\breast_cancer_project\models\best_model_sanitized.keras"

try:
    print(f"Attempting to load SANITIZED model from {MODEL_PATH}...")
    model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    print("SUCCESS! Model loaded in Keras 3.")
    model.summary()
except Exception as e:
    print(f"FAILURE: {e}")
