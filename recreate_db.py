from flask import Flask
from app.models.models import db, User, Artist, Artwork, Vote
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///art_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def recreate_database():
    with app.app_context():
        # Supprimer la base de données si elle existe
        if os.path.exists('art_database.db'):
            os.remove('art_database.db')
            print("Base de données supprimée")
        
        # Supprimer toutes les tables existantes
        db.drop_all()
        print("Tables supprimées")
        
        # Créer les nouvelles tables
        db.create_all()
        print("Tables créées")
        
        # Créer l'utilisateur admin
        admin = User(
            username='admin_cartel',
            email='admin@artcartel.com',
            is_admin=True
        )
        admin.set_password('AdminCartel2025!')
        db.session.add(admin)

        # Créer des membres
        membres = [
            User(username='membre1', email='membre1@artcartel.com', is_membre=True),
            User(username='membre2', email='membre2@artcartel.com', is_membre=True),
            User(username='membre3', email='membre3@artcartel.com', is_membre=True)
        ]
        for membre in membres:
            membre.set_password(f'{membre.username}Cartel2025!')
            db.session.add(membre)

        # Créer des artistes
        artistes = [
            User(username='artiste1', email='artiste1@artcartel.com', is_artiste=True),
            User(username='artiste2', email='artiste2@artcartel.com', is_artiste=True)
        ]
        for artiste in artistes:
            artiste.set_password(f'{artiste.username}Cartel2025!')
            db.session.add(artiste)

        db.session.commit()
        print("Utilisateurs créés")

if __name__ == '__main__':
    recreate_database()
