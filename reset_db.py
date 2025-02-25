from app import create_app
from app.models.models import db, User, Artist, Artwork
import os

def reset_database():
    app = create_app()
    with app.app_context():
        # Supprimer la base de données existante
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"Base de données supprimée : {db_path}")
        
        # Créer toutes les tables
        db.create_all()
        print("Tables créées avec succès")
        
        # Créer l'utilisateur admin
        admin = User(
            username='admin',
            email='admin@example.com',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Créer un compte membre de test
        member = User(
            username='membre',
            email='membre@example.com',
            is_admin=False
        )
        member.set_password('membre123')
        db.session.add(member)
        
        # Créer quelques artistes de test
        artist1 = Artist(
            nom='Dubois',
            prenom='Marie',
            nom_artiste='MDubois',
            email='marie.dubois@example.com',
            telephone='0123456789',
            adresse='123 rue de l\'Art',
            code_postal='75001',
            ville='Paris',
            edition_email=True,
            edition_telephone=True
        )
        
        artist2 = Artist(
            nom='Martin',
            prenom='Pierre',
            nom_artiste='PMartin',
            email='pierre.martin@example.com',
            telephone='0987654321',
            adresse='456 avenue des Arts',
            code_postal='75002',
            ville='Paris',
            edition_email=True
        )
        
        db.session.add(artist1)
        db.session.add(artist2)
        db.session.commit()
        
        # Créer quelques œuvres de test
        artwork1 = Artwork(
            artist_id=artist1.id,
            numero='A001',
            titre='Nature morte aux fruits',
            technique='Huile sur toile',
            dimension_largeur=60,
            dimension_hauteur=80,
            prix=1200,
            description='Nature morte représentant des fruits dans un panier'
        )
        
        artwork2 = Artwork(
            artist_id=artist1.id,
            numero='A002',
            titre='Paysage urbain',
            technique='Acrylique sur toile',
            dimension_largeur=100,
            dimension_hauteur=120,
            prix=2500,
            description='Vue panoramique d\'une ville moderne'
        )
        
        artwork3 = Artwork(
            artist_id=artist2.id,
            numero='A003',
            titre='Abstraction #1',
            technique='Technique mixte',
            dimension_largeur=80,
            dimension_hauteur=80,
            prix=1800,
            description='Composition abstraite en bleu et rouge'
        )
        
        db.session.add(artwork1)
        db.session.add(artwork2)
        db.session.add(artwork3)
        db.session.commit()
        
        print("Données de test créées avec succès")

if __name__ == '__main__':
    reset_database()
