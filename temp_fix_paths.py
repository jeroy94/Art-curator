from app import create_app
from app.models.models import Artwork, db

app = create_app()

with app.app_context():
    artworks = Artwork.query.all()
    for artwork in artworks:
        if artwork.photo_path and artwork.photo_path.startswith('uploads/'):
            # Enlever 'uploads/' du chemin
            artwork.photo_path = artwork.photo_path[8:]
    db.session.commit()
    print("Chemins corrigés avec succès")
