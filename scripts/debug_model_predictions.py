import glob, os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.resnet50 import preprocess_input

VAL_DIR = os.path.join('data','val')
if not os.path.exists(VAL_DIR) or not any(os.scandir(VAL_DIR)):
    VAL_DIR = os.path.join('data','test')

print('Using VAL_DIR ->', VAL_DIR)

datagen = ImageDataGenerator(preprocessing_function=preprocess_input)
gen = datagen.flow_from_directory(VAL_DIR, target_size=(224,224), batch_size=16, class_mode='binary', shuffle=False)

ckpts = glob.glob('models/*.keras') + glob.glob('models/*.h5')
if not ckpts:
    raise SystemExit('No model files found in models/')
ckpts.sort(key=os.path.getmtime, reverse=True)
model_path = ckpts[0]
print('Loading model:', model_path)
model = tf.keras.models.load_model(model_path)
try:
    print('Model output layer:', model.layers[-1].name)
    print('Model output shape:', model.output_shape)
except Exception:
    print('Could not read model output shape')

# Get one batch
x, y = next(gen)
preds = model.predict(x)
print('Predictions shape:', preds.shape)
import numpy as _np
_np.set_printoptions(precision=18, suppress=False)
print('Predictions sample (first 16) repr:', repr(preds.flatten()[:16]))
print('Predictions as float64:', preds.astype(_np.float64).flatten()[:16])
print('Predictions min/max:', float(preds.min()), float(preds.max()))
print('Labels sample (first 10):', y[:10])

# If predictions are integers or all identical, show unique values
print('Unique pred values:', np.unique(preds))
print('Input batch stats: min/max/mean:', x.min(), x.max(), x.mean())
try:
    import tensorflow as _tf
    tpred = model(_tf.convert_to_tensor(x), training=False).numpy()
    print('Direct call output unique:', _np.unique(tpred))
except Exception as e:
    print('Direct call failed:', e)
# Inspect intermediate output (head before final dense)
try:
    penult = model.layers[-3]
    inter_model = tf.keras.Model(inputs=model.input, outputs=penult.output)
    ival = inter_model.predict(x)
    print('Intermediate output shape:', ival.shape)
    print('Intermediate stats min/max/mean:', ival.min(), ival.max(), ival.mean())
except Exception as e:
    print('Could not compute intermediate output:', e)
try:
    last = model.layers[-1]
    w, b = last.get_weights()
    print('Last dense weights shape:', w.shape, 'bias shape:', b.shape)
    print('weights min/max/mean:', w.min(), w.max(), w.mean())
    print('bias min/max/mean:', b.min(), b.max(), b.mean())
    # manual forward for final dense
    wp, bp = w, b
    logits = ival.dot(wp) + bp
    def _sig(x):
        return 1.0 / (1.0 + _np.exp(-x))
    manual = _sig(logits)
    print('Manual final preds min/max/mean:', manual.min(), manual.max(), manual.mean())
    print('Manual sample:', manual.flatten()[:10])
except Exception as e:
    print('Could not inspect last layer weights or manual forward failed:', e)
try:
    act = getattr(last, 'activation', None)
    print('Last layer activation:', getattr(act, '__name__', str(act)))
except Exception:
    pass
print('Last 6 layers:')
for l in model.layers[-6:]:
    print('  ', l.name, type(l))
