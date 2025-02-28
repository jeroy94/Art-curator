from app import create_app
from app.models.models import db, User
from werkzeug.security import generate_password_hash

def create_users():
    app = create_app()
    with app.app_context():
        # Supprimer les utilisateurs existants
        User.query.delete()
        
        # Créer un compte administrateur
        admin = User(
            username='admin',
            email='admin@artcartel.com',
            is_admin=True
        )
        admin.password_hash = generate_password_hash('AdminCartel2025!')
        db.session.add(admin)
        
        # Créer des comptes membres
        membres = [
            {'username': 'membre1', 'email': 'membre1@artcartel.com', 'is_admin': False},
            {'username': 'membre2', 'email': 'membre2@artcartel.com', 'is_admin': False},
            {'username': 'membre3', 'email': 'membre3@artcartel.com', 'is_admin': False}
        ]
        
        for membre_data in membres:
            membre = User(
                username=membre_data['username'],
                email=membre_data['email'],
                is_admin=membre_data['is_admin']
            )
            membre.password_hash = generate_password_hash(f"{membre_data['username']}Cartel2025!")
            db.session.add(membre)
        
        db.session.commit()
        print("Utilisateurs créés avec succès !")
        
        # Afficher les détails des utilisateurs
        print("\nUtilisateurs créés :")
        users = User.query.all()
        for user in users:
            print(f"Username: {user.username}, Email: {user.email}, Admin: {user.is_admin}")

if __name__ == '__main__':
    create_users()
