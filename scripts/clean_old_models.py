import os
import glob

ROOT = os.path.dirname(os.path.dirname(__file__))
MODELS_DIR = os.path.join(ROOT, "models")

patterns = [
    os.path.join(MODELS_DIR, "resnet_cancer_epoch_*.keras"),
    os.path.join(MODELS_DIR, "resnet_cancer*.h5"),
    os.path.join(MODELS_DIR, "resnet_cancer_best.keras"),
]

removed = []
for pat in patterns:
    for path in glob.glob(pat):
        try:
            os.remove(path)
            removed.append(path)
        except Exception as e:
            print(f"Failed to remove {path}: {e}")

if removed:
    print("Removed files:")
    for p in removed:
        print(" -", p)
else:
    print("No matching old checkpoints found.")
