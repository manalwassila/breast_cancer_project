import os
import zipfile
import json
import shutil

MODEL_PATH = r"c:\Users\manal\breast_cancer_project\models\best_model.keras"
SANITIZED_PATH = r"c:\Users\manal\breast_cancer_project\models\best_model_sanitized.keras"
TEMP_DIR = r"c:\Users\manal\breast_cancer_project\models\temp_model"

def sanitize_keras_model(input_path, output_path):
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR)

    print(f"Unzipping {input_path}...")
    with zipfile.ZipFile(input_path, 'r') as zip_ref:
        zip_ref.extractall(TEMP_DIR)

    config_path = os.path.join(TEMP_DIR, 'config.json')
    if not os.path.exists(config_path):
        print("❌ No config.json found in model!")
        return

    print("Reading and cleaning config.json...")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # Convert to string to do a global replace or traverse the dict
    config_str = json.dumps(config)
    
    # Offending keys in Keras 3 for BatchNormalization
    offending_keys = ['"renorm": false', '"renorm": True', '"renorm_clipping": null', '"renorm_momentum": 0.99']
    
    # We'll do a more surgical replacement if possible, but let's try traversal
    def clean_dict(d):
        if not isinstance(d, (dict, list)):
            return d
        if isinstance(d, list):
            return [clean_dict(x) for x in d]
        
        new_d = {}
        for k, v in d.items():
            if k in ['renorm', 'renorm_clipping', 'renorm_momentum']:
                print(f"Removing key: {k}")
                continue
            new_d[k] = clean_dict(v)
        return new_d

    clean_config = clean_dict(config)

    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(clean_config, f)

    print(f"Re-zipping to {output_path}...")
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
        for root, dirs, files in os.walk(TEMP_DIR):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), TEMP_DIR)
                zip_ref.write(os.path.join(root, file), rel_path)

    print("✅ Done!")
    shutil.rmtree(TEMP_DIR)

sanitize_keras_model(MODEL_PATH, SANITIZED_PATH)
