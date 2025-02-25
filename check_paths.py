from app import create_app
from app.models.models import Artwork

app = create_app()

with app.app_context():
    artworks = Artwork.query.all()
    print("Chemins des photos dans la base de données :")
    for artwork in artworks:
        print(f"Titre: {artwork.titre}")
        print(f"Chemin photo: {artwork.photo_path}")
        print("-" * 50)
