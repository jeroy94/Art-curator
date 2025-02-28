from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.models.models import db, User, Base
import logging

logger = logging.getLogger(__name__)

class Invitation(db.Model):
    """Modèle pour les invitations utilisateur."""
    __tablename__ = 'invitations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    role = db.Column(db.String(20), nullable=False)
    token = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)

def create_tables(engine):
    """Créer toutes les tables de la base de données."""
    # Utiliser Base.metadata pour créer les tables définies par les modèles SQLAlchemy
    Base.metadata.create_all(engine)
    logger.info("Tables créées avec succès")

def init_database(app=None):
    """
    Initialiser la base de données avec des utilisateurs par défaut
    """
    if app is None:
        from flask import current_app
        app = current_app

    with app.app_context():
        try:
            # Créer toutes les tables
            create_tables(db.engine)
            
            # Vérifier et créer l'utilisateur admin si nécessaire
            admin_email = app.config.get('ADMIN_EMAIL', 'admin@artcartel.com')
            admin_user = User.query.filter_by(email=admin_email).first()
            
            if not admin_user:
                # Créer un utilisateur admin par défaut
                admin_user = User(
                    email=admin_email,
                    username='admin',
                    is_admin=True
                )
                # Définir un mot de passe temporaire
                admin_user.set_password('AdminTempPass123!')
                
                db.session.add(admin_user)
                db.session.commit()
                logger.info(f"Utilisateur admin créé : {admin_email}")
        
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de la base de données : {e}")
            raise

def reset_database(app=None):
    """
    Réinitialiser complètement la base de données
    Si aucune app n'est fournie, utiliser current_app
    """
    if app is None:
        from flask import current_app
        app = current_app

    with app.app_context():
        try:
            db.drop_all()
            logger.info("Toutes les tables ont été supprimées")
            
            db.create_all()
            logger.info("Toutes les tables ont été recréées")
            
            init_database(app)
        
        except Exception as e:
            logger.error(f"Erreur lors de la réinitialisation de la base de données : {e}")
            raise