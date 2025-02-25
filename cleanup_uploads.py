import os
import shutil
from pathlib import Path

def cleanup_uploads():
    # Définir le dossier cible (le seul que nous voulons garder)
    app_root = Path('F:/image_to_3d/app')
    target_dir = app_root / 'static' / 'uploads'
    target_artworks_dir = target_dir / 'artworks'
    
    # Créer les dossiers cibles s'ils n'existent pas
    target_dir.mkdir(parents=True, exist_ok=True)
    target_artworks_dir.mkdir(parents=True, exist_ok=True)
    
    # Liste des dossiers à nettoyer
    dirs_to_clean = [
        Path('F:/image_to_3d/uploads'),
        Path('F:/image_to_3d/static/uploads'),
        Path('F:/image_to_3d/app/static/images')  # On garde que no-image.png
    ]
    
    # Déplacer les fichiers vers le bon dossier
    for source_dir in dirs_to_clean:
        if source_dir.exists():
            print(f"\nTraitement de {source_dir}...")
            
            # Parcourir tous les fichiers du dossier
            for file_path in source_dir.rglob('*'):
                if file_path.is_file():
                    # Si c'est no-image.png, on le déplace dans static/images
                    if file_path.name == 'no-image.png':
                        images_dir = app_root / 'static' / 'images'
                        images_dir.mkdir(parents=True, exist_ok=True)
                        target_path = images_dir / file_path.name
                    else:
                        # Sinon, on le déplace dans static/uploads/artworks
                        target_path = target_artworks_dir / file_path.name
                    
                    try:
                        print(f"Déplacement de {file_path} vers {target_path}")
                        shutil.copy2(file_path, target_path)
                    except Exception as e:
                        print(f"Erreur lors du déplacement de {file_path}: {e}")
    
    # Supprimer les anciens dossiers
    for dir_path in dirs_to_clean:
        if dir_path != app_root / 'static' / 'images' and dir_path.exists():
            try:
                print(f"\nSuppression de {dir_path}")
                shutil.rmtree(dir_path)
            except Exception as e:
                print(f"Erreur lors de la suppression de {dir_path}: {e}")

if __name__ == '__main__':
    print("Début du nettoyage des dossiers d'upload...")
    cleanup_uploads()
    print("\nNettoyage terminé !")
