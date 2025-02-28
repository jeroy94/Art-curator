import os
import sys
import traceback
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models.models import db, Artist, Artwork, User

def populate_database():
    app = create_app()
    
    with app.app_context():
        try:
            # Supprimer les données existantes
            Artwork.query.delete()
            Artist.query.delete()
            
            # Créer des artistes
            artists = [
                Artist(
                    nom='Dupont', 
                    prenom='Jean', 
                    nom_artiste='Jean Dupont',
                    email='jean.dupont@example.com'
                ),
                Artist(
                    nom='Martin', 
                    prenom='Sophie', 
                    nom_artiste='Sophie Martin',
                    email='sophie.martin@example.com'
                )
            ]
            
            db.session.add_all(artists)
            db.session.flush()  # Pour obtenir les ID
            
            # Créer des œuvres avec des statuts corrects
            artworks = [
                Artwork(
                    titre='Paysage Abstrait',
                    description='Une œuvre abstraite représentant un paysage',
                    technique='Huile sur toile',
                    materiaux='Toile, Huile',
                    annee_creation=2023,
                    dimension_largeur=100,
                    dimension_hauteur=80,
                    prix=1500,
                    statut='en_attente',  # Statut correct
                    artist_id=artists[0].id
                ),
                Artwork(
                    titre='Portrait Moderne',
                    description='Un portrait contemporain',
                    technique='Acrylique',
                    materiaux='Toile, Acrylique',
                    annee_creation=2022,
                    dimension_largeur=90,
                    dimension_hauteur=70,
                    prix=2000,
                    statut='selectionne',  # Statut correct
                    artist_id=artists[1].id
                ),
                Artwork(
                    titre='Nature Morte',
                    description='Composition de fruits et objets',
                    technique='Aquarelle',
                    materiaux='Papier, Aquarelle',
                    annee_creation=2024,
                    dimension_largeur=60,
                    dimension_hauteur=50,
                    prix=800,
                    statut='en_attente',  # Statut correct
                    artist_id=artists[0].id
                )
            ]
            
            db.session.add_all(artworks)
            db.session.commit()
            
            print("Base de données peuplée avec succès !")
            
            # Vérification
            print(f"Nombre d'artistes : {Artist.query.count()}")
            print(f"Nombre d'œuvres : {Artwork.query.count()}")
            
            for artwork in Artwork.query.all():
                print(f"Œuvre : {artwork.titre}, Statut : {artwork.statut}")
        
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors du peuplement de la base de données : {e}")
            traceback.print_exc()

if __name__ == '__main__':
    populate_database()
