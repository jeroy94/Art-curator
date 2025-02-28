from app import create_app
from app.models.models import db, User

def create_admin():
    app = create_app()
    with app.app_context():
        # Vérifier si un admin existe déjà
        existing_admin = User.query.filter_by(is_admin=True).first()
        if existing_admin:
            print("Un compte administrateur existe déjà.")
            return

        # Créer un nouvel admin
        admin = User(
            username='admin',
            email='admin@artcartel.com',
            is_admin=True
        )
        admin.set_password('admin_password')  # À changer impérativement !
        
        db.session.add(admin)
        db.session.commit()
        
        print("Compte administrateur créé avec succès !")

if __name__ == '__main__':
    create_admin()
