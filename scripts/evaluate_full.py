import os, glob, numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.resnet50 import preprocess_input

TRAIN_DIR=os.path.join('data','train')
VAL_DIR=os.path.join('data','val')
if not os.path.exists(VAL_DIR) or not any(os.scandir(VAL_DIR)):
    VAL_DIR=os.path.join('data','test')

BATCH_SIZE=32
IMG_SIZE=(224,224)

print('Using VAL_DIR ->', VAL_DIR)

val_datagen=ImageDataGenerator(preprocessing_function=preprocess_input)
val_gen=val_datagen.flow_from_directory(VAL_DIR, target_size=IMG_SIZE, batch_size=BATCH_SIZE, class_mode='binary', shuffle=False)

ckpts=glob.glob('models/*.keras')+glob.glob('models/*.h5')
if not ckpts:
    raise SystemExit('No model files found in models/')
ckpts.sort(key=os.path.getmtime, reverse=True)
latest=ckpts[0]
print('Loading model:', latest)
model=tf.keras.models.load_model(latest)
print(model.summary())

steps=len(val_gen)
print('Val steps:', steps, 'images:', steps*BATCH_SIZE)

# Predict
probs = model.predict(val_gen, steps=steps, verbose=1)
probs = probs.ravel()

# Ground-truth labels (flow_from_directory preserves order when shuffle=False)
if hasattr(val_gen, 'classes'):
    y_true = np.array(val_gen.classes)
else:
    # fallback: rebuild labels from filenames
    y_true = []
    for i in range(steps):
        _, yb = next(val_gen)
        y_true.extend(yb)
    y_true = np.array(y_true[:len(probs)])

# Align lengths
minlen = min(len(probs), len(y_true))
probs = probs[:minlen]
y_true = y_true[:minlen]

# Predicted labels
y_pred = (probs >= 0.5).astype(int)

# Compute metrics
try:
    from sklearn.metrics import confusion_matrix, classification_report, roc_auc_score
    cm = confusion_matrix(y_true, y_pred)
    print('Confusion matrix:\n', cm)
    print('\nClassification report:\n', classification_report(y_true, y_pred, digits=4))
    try:
        auc = roc_auc_score(y_true, probs)
        print('\nROC AUC:', auc)
    except Exception as e:
        print('Failed to compute roc_auc_score:', e)
except Exception as e:
    print('sklearn not available, falling back to tensorflow metrics:', e)
    cm0 = np.zeros((2,2), dtype=int)
    for t,p in zip(y_true, y_pred):
        cm0[int(t), int(p)] += 1
    print('Confusion matrix:\n', cm0)
    auc_metric = tf.keras.metrics.AUC()
    auc_metric.update_state(y_true, probs)
    print('\nROC AUC (tf):', float(auc_metric.result().numpy()))

# Summary counts
pos = int(y_true.sum())
neg = len(y_true)-pos
print('\nValidation samples: total=', len(y_true), 'positive=', pos, 'negative=', neg)

# Save predictions to CSV
out_csv = 'results/val_predictions.csv'
os.makedirs('results', exist_ok=True)
import csv
with open(out_csv, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['filename','true','prob','pred'])
    fnames = val_gen.filenames
    for i in range(minlen):
        w.writerow([fnames[i], int(y_true[i]), float(probs[i]), int(y_pred[i])])
print('Wrote predictions to', out_csv)
