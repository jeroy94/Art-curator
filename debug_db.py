import os
import sys
import traceback

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app import create_app
from app.models.models import Artwork, Artist

# Créer l'application
app = create_app()

try:
    with app.app_context():
        print('Informations détaillées sur la base de données :')
        
        # Nombre total d'œuvres
        total_artworks = Artwork.query.count()
        print(f'\nNombre total d\'œuvres : {total_artworks}')
        
        # Récupérer tous les statuts
        all_artworks = Artwork.query.all()
        statuts = set(artwork.statut for artwork in all_artworks)
        
        print('\nStatuts des œuvres :')
        for statut in statuts:
            count = len([a for a in all_artworks if a.statut == statut])
            print(f'  - {statut} : {count} œuvres')
        
        # Détails des œuvres
        print('\nDétails des œuvres :')
        for artwork in all_artworks:
            try:
                artist = Artist.query.get(artwork.artist_id)
                print(f'Œuvre {artwork.id}:')
                print(f'  - Titre : {artwork.titre}')
                print(f'  - Statut : {artwork.statut}')
                print(f'  - Artiste : {artist.nom_artiste if artist else "N/A"}')
                print('---')
            except Exception as artist_error:
                print(f"Erreur lors de la récupération de l'artiste pour l'œuvre {artwork.id}: {artist_error}")

except Exception as e:
    print(f"Erreur inattendue : {e}")
    traceback.print_exc()
