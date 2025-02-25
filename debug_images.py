from app import create_app
from app.models.models import Artwork
import os

app = create_app()

with app.app_context():
    artworks = Artwork.query.all()
    print("\nInformations des œuvres dans la base de données:")
    for artwork in artworks:
        print(f"\nTitre: {artwork.titre}")
        print(f"Chemin stocké: {artwork.photo_path}")
        
        # Vérifier si le fichier existe dans le système
        if artwork.photo_path:
            full_path = os.path.join(app.root_path, 'static', artwork.photo_path)
            exists = os.path.exists(full_path)
            print(f"Chemin complet: {full_path}")
            print(f"Le fichier existe: {exists}")
            
            if exists:
                print(f"Taille du fichier: {os.path.getsize(full_path)} bytes")
