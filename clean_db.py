from app import create_app
from app.models.models import db, Artwork, Artist

app = create_app()

with app.app_context():
    # Supprimer toutes les œuvres
    Artwork.query.delete()
    # Supprimer tous les artistes
    Artist.query.delete()
    # Sauvegarder les changements
    db.session.commit()
    print("Base de données nettoyée avec succès")
