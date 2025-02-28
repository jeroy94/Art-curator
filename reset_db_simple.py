from app import create_app
from app.models.models import db, User
import os

def reset_database():
    app = create_app()
    with app.app_context():
        # Supprimer la base de données existante
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        if os.path.exists(db_path):
            os.remove(db_path)
        
        # Recréer les tables
        db.create_all()

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

        # Commit des utilisateurs
        db.session.commit()
        print("Base de données réinitialisée avec succès !")

if __name__ == '__main__':
    reset_database()
