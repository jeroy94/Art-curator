from app import create_app
from app.models.models import Artwork, db

app = create_app()

with app.app_context():
    artworks = Artwork.query.all()
    for artwork in artworks:
        if artwork.photo_path and 'artworks/artworks/' in artwork.photo_path:
            # Corriger le doublon
            artwork.photo_path = artwork.photo_path.replace('artworks/artworks/', 'artworks/')
    db.session.commit()
    print("Chemins corrigés avec succès")
    
    # Afficher les chemins actuels
    for artwork in Artwork.query.all():
        print(f"ID: {artwork.id}, Photo Path: {artwork.photo_path}")
