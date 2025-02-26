import os
import sys

# Ajouter le répertoire parent au chemin de Python
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from app import create_app
from app.models.models import db, Artist

def normalize_existing_artists():
    app = create_app()
    with app.app_context():
        # Récupérer tous les artistes
        artists = Artist.query.all()
        
        for artist in artists:
            # Normaliser les noms
            artist.nom = Artist.normalize_name(artist.nom)
            artist.prenom = Artist.normalize_name(artist.prenom)
            
            if artist.nom_artiste:
                artist.nom_artiste = Artist.normalize_name(artist.nom_artiste)
            
            if artist.prenom_artiste:
                artist.prenom_artiste = Artist.normalize_name(artist.prenom_artiste)
        
        # Commit des modifications
        db.session.commit()
        print(f"Normalisé {len(artists)} artistes")

if __name__ == '__main__':
    normalize_existing_artists()
