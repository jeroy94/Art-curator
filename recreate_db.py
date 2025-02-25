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
            username='admin',
            email='admin@exposition-art.com',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Utilisateur admin créé")

if __name__ == '__main__':
    recreate_database()
