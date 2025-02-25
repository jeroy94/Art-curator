from app import create_app
from app.models.models import Artwork, db

app = create_app()

with app.app_context():
    artworks = Artwork.query.all()
    for artwork in artworks:
        print(f"ID: {artwork.id}, Photo Path: {artwork.photo_path}")
