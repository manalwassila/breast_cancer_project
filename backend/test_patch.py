import tensorflow as tf
import keras
import os

MODEL_PATH = r"c:\Users\manal\breast_cancer_project\models\best_model.keras"

# Patch for Keras 2 -> Keras 3 compatibility
class LegacyBatchNormalization(keras.layers.BatchNormalization):
    def __init__(self, **kwargs):
        # Remove arguments that Keras 3 doesn't recognize
        kwargs.pop('renorm', None)
        kwargs.pop('renorm_clipping', None)
        kwargs.pop('renorm_momentum', None)
        super().__init__(**kwargs)

try:
    print(f"Attempting to load model with LegacyBatchNormalization patch...")
    # Register the patch
    with keras.utils.custom_object_scope({'BatchNormalization': LegacyBatchNormalization}):
        model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    
    print("✅ Model loaded successfully with patch!")
    model.summary()
except Exception as e:
    print(f"❌ Failed even with patch: {e}")

    # Alternative: try loading as a functional model config if possible
    print("\nTrying alternative: Loading from config manual cleanup...")
    try:
         import json
         import h5py
         import zipfile

         # For .keras files (which are zip), we'd need to unzip and edit config.json
         # But let's see if we can use the high-level API first.
         pass
    except Exception as e2:
         print(f"Secondary failure: {e2}")
