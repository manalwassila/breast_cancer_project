import gradio as gr
import tensorflow as tf
import numpy as np
import os
from PIL import Image

# Chemin vers le modèle — préférer le meilleur checkpoint .keras, sinon h5
_models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models'))
_candidates = [
    os.path.join(_models_dir, 'resnet_cancer_best.keras'),
    os.path.join(_models_dir, 'resnet_cancer.h5'),
]
MODEL_PATH = next((p for p in _candidates if os.path.exists(p)), None)

# Tentative de chargement du modèle
try:
    if MODEL_PATH:
        model = tf.keras.models.load_model(MODEL_PATH)
        model_loaded = True
        print(f"✅ Modèle chargé : {os.path.basename(MODEL_PATH)}")
    else:
        model_loaded = False
        model = None
        print("⏳ Aucun modèle trouvé. En attente de la fin de l'entraînement...")
except Exception as e:
    model_loaded = False
    model = None
    print(f"⚠️ Erreur lors du chargement : {e}")

def predict_cancer(image):
    if not model_loaded:
        return "⚠️ Le modèle est encore en cours d'entraînement ! Revenez quand resnet_cancer.h5 sera prêt."
    
    try:
        # Prétraitement de l'image (identique à ImageDataGenerator : target_size 224x224 et rescale 1/255)
        img = image.resize((224, 224))
        img_array = np.array(img, dtype=np.float32)
        
        # Rescale pour que les pixels soient entre 0 et 1
        img_array = img_array / 255.0
        
        # Ajouter la dimension du batch : de (224, 224, 3) à (1, 224, 224, 3)
        img_array = np.expand_dims(img_array, axis=0)
        
        # Inférence
        prediction = model.predict(img_array)[0][0]
        
        # Interprétation du résultat (binaire : > 0.5 = classe 1, <= 0.5 = classe 0)
        # NB: ImageDataGenerator trie les dossiers par ordre alphabétique :
        # Dossier B (Benign) = 0, Dossier M (Malignant) = 1 (A vérifier avec tes dossiers)
        if prediction >= 0.5:
            confidence = prediction * 100
            label = "Maligne 🚨"
            return {label: prediction, "Bénigne ✅": 1 - prediction}
        else:
            confidence = (1 - prediction) * 100
            label = "Bénigne ✅"
            return {"Bénigne ✅": 1 - prediction, "Maligne 🚨": prediction}
            
    except Exception as e:
        return f"Erreur lors de la prédiction : {str(e)}"

# Construction de l'interface visuelle avec un joli thème
with gr.Blocks(theme=gr.themes.Soft(primary_hue="blue", neutral_hue="slate")) as demo:
    gr.Markdown("<h1 style='text-align: center; color: #1e3a8a;'>🩺 IA Experte - Diagnostic Cancer du Sein (ResNet50)</h1>")
    gr.Markdown("<p style='text-align: center; font-size: 16px;'>Uploadez une image histopathologique ou une radiographie. L'algorithme (précision ~98%) analysera les tissus pour prédire la présence d'une tumeur.</p>")
    
    with gr.Row():
        with gr.Column():
            image_input = gr.Image(type="pil", label="Importer votre image médicale", height=400)
            submit_btn = gr.Button("🔍 Lancer le diagnostic IA", variant="primary")
        with gr.Column():
            result_output = gr.Label(label="Résultat de l'analyse", num_top_classes=2)
            
    gr.Markdown("*(Avertissement: Cette application expérimentale dans le cadre d'un PFA ne remplace pas l'avis d'un professionnel de santé professionnel.)*")
    
    # Lien entre le bouton et la fonction
    submit_btn.click(predict_cancer, inputs=image_input, outputs=result_output)

# Lancement
if __name__ == "__main__":
    demo.launch(share=False)
