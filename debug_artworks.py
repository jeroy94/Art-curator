import os
import sys

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

# Créer l'application et initialiser la base de données
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

from app.models.models import Artwork, Artist

with app.app_context():
    print('Nombre total d\'œuvres :', Artwork.query.count())
    print('Statuts d\'œuvres :')
    statuts = db.session.query(Artwork.statut).distinct().all()
    for statut in statuts:
        print(f'  - {statut[0]} : {Artwork.query.filter_by(statut=statut[0]).count()} œuvres')
    
    print('\nDétails des œuvres :')
    artworks = Artwork.query.all()
    for artwork in artworks:
        artist = Artist.query.get(artwork.artist_id)
        print(f'Œuvre {artwork.id}: Titre="{artwork.titre}", Statut={artwork.statut}, Artiste={artist.nom_artiste if artist else "N/A"}')
