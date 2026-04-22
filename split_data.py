import os
import shutil
import random

# Fixer le seed pour être reproductible
random.seed(42)

def split_dataset(train_dir, test_dir, split_ratio=0.2):
    
    print(f"🚀 Début de la séparation des données (Ratio de Test: {split_ratio*100}%)")
    
    classes = ['benign', 'malignant']
    
    for cls in classes:
        train_cls_dir = os.path.join(train_dir, cls)
        test_cls_dir = os.path.join(test_dir, cls)
        
        # S'assurer que le dossier de test existe
        os.makedirs(test_cls_dir, exist_ok=True)
        
        # Lister toutes les images présentes dans le dossier d'entraînement pour cette classe
        if not os.path.exists(train_cls_dir):
            print(f"⚠️ Le dossier {train_cls_dir} n'existe pas.")
            continue
            
        images = os.listdir(train_cls_dir)
        num_images = len(images)
        
        if num_images == 0:
            print(f"⚠️ Aucune image dans {train_cls_dir}. (Peut-être qu'elles sont déjà triées ?)")
            continue
            
        # Calculer le nombre d'images à déplacer (20%)
        num_test = int(num_images * split_ratio)
        
        # Sélection aléatoire des fichiers
        test_images = random.sample(images, num_test)
        
        print(f"👉 Déplacement de {num_test} images de la classe '{cls}' vers {test_cls_dir}... (Patientez quelques secondes)")
        
        # Déplacer physiquement les fichiers
        for img in test_images:
            src = os.path.join(train_cls_dir, img)
            dst = os.path.join(test_cls_dir, img)
            shutil.move(src, dst)
            
    print("✅ Séparation terminée avec succès ! Le dossier `data/test` est prêt.")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    train_directory = os.path.join(current_dir, 'data', 'train')
    test_directory = os.path.join(current_dir, 'data', 'test')
    
    split_dataset(train_directory, test_directory)
