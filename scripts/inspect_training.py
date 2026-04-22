import os, glob, numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.resnet50 import preprocess_input

TRAIN_DIR=os.path.join('data','train')
VAL_DIR=os.path.join('data','val')
if not os.path.exists(VAL_DIR) or not any(os.scandir(VAL_DIR)):
    VAL_DIR=os.path.join('data','test')

print('Using VAL_DIR ->', VAL_DIR)

def count_classes(dirpath):
    d={}
    if not os.path.exists(dirpath):
        return d
    for c in sorted(os.listdir(dirpath)):
        p=os.path.join(dirpath,c)
        if os.path.isdir(p):
            cnt=sum(1 for _ in glob.iglob(os.path.join(p,'**','*.*'), recursive=True))
            d[c]=cnt
    return d

print('train class counts:', count_classes(TRAIN_DIR))
print('val class counts:  ', count_classes(VAL_DIR))

BATCH_SIZE=32
IMG_SIZE=(224,224)

train_datagen=ImageDataGenerator(preprocessing_function=preprocess_input)
train_gen=train_datagen.flow_from_directory(TRAIN_DIR, target_size=IMG_SIZE, batch_size=BATCH_SIZE, class_mode='binary', shuffle=True)

val_datagen=ImageDataGenerator(preprocessing_function=preprocess_input)
val_gen=val_datagen.flow_from_directory(VAL_DIR, target_size=IMG_SIZE, batch_size=BATCH_SIZE, class_mode='binary', shuffle=False)

x,y=next(train_gen)
print('sample batch shapes:', x.shape, y.shape)
print('sample batch labels unique:', np.unique(y, return_counts=True))

ckpts=glob.glob('models/*.keras')+glob.glob('models/*.h5')
if ckpts:
    ckpts.sort(key=os.path.getmtime, reverse=True)
    latest=ckpts[0]
    print('Found model file:', latest)
    try:
        model=tf.keras.models.load_model(latest)
        steps=min(20, len(val_gen))
        print('Evaluating on val for', steps, 'steps...')
        res=model.evaluate(val_gen, steps=steps, verbose=1)
        print('Evaluation results:', res)
    except Exception as e:
        print('Failed to load/evaluate model:', e)
else:
    print('No model files found in models/ to evaluate.')
