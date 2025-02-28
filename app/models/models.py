from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import current_app
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, text
import logging
import os

logger = logging.getLogger(__name__)

db = SQLAlchemy()
Base = declarative_base()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_membre = db.Column(db.Boolean, default=False)
    is_artiste = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

def reset_database(app):
    with app.app_context():
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        if os.path.exists(db_path):
            os.remove(db_path)
            logger.info(f"Base de données supprimée : {db_path}")
        
        db.create_all()
        logger.info("Tables créées avec succès")
        
        create_admin_user(app)

def reset_database_full(app):
    """
    Réinitialise complètement la base de données.
    Supprime toutes les tables et les recrée.
    """
    with app.app_context():
        # Supprimer toutes les tables
        db.drop_all()
        
        # Recréer toutes les tables
        db.create_all()
        
        logger.info("Base de données réinitialisée complètement")
        
        # Recréer l'utilisateur admin et les utilisateurs de test
        create_admin_user(app)
        create_test_users(app)

class Artist(db.Model):
    __tablename__ = 'artists'
    
    id = db.Column(db.Integer, primary_key=True)
    numero_dossier = db.Column(db.String(50), unique=True, nullable=True)
    civilite = db.Column(db.String(10), default='')
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    nom_artiste = db.Column(db.String(100), default='')
    prenom_artiste = db.Column(db.String(100), default='')
    adresse = db.Column(db.String(200), default='')
    code_postal = db.Column(db.String(10), default='')
    ville = db.Column(db.String(100), default='')
    pays = db.Column(db.String(100), default='France')
    telephone = db.Column(db.String(20), default='')
    email = db.Column(db.String(120), unique=True, nullable=False)
    site_internet = db.Column(db.String(200), default='')
    facebook = db.Column(db.String(200), default='')
    numero_mda = db.Column(db.String(50), default='')
    numero_siret = db.Column(db.String(50), default='')
    categorie = db.Column(db.String(50), default='')
    edition_adresse = db.Column(db.Boolean, default=False, nullable=False)
    edition_telephone = db.Column(db.Boolean, default=False, nullable=False)
    edition_email = db.Column(db.Boolean, default=False, nullable=False)
    edition_site = db.Column(db.Boolean, default=False, nullable=False)
    edition_facebook = db.Column(db.Boolean, default=False, nullable=False)
    nom_catalogue = db.Column(db.String(200), default='', nullable=True)
    qr_code_link = db.Column(db.String(200), default='', nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relation avec les œuvres
    artworks = db.relationship('Artwork', backref='artist', lazy=True)

    @classmethod
    def normalize_name(cls, name):
        """
        Normalise un nom ou un prénom en mettant la première lettre en majuscule 
        et le reste en minuscules.
        
        Args:
            name (str): Le nom ou prénom à normaliser
        
        Returns:
            str: Le nom normalisé
        """
        if not name:
            return name
        
        # Séparer les parties du nom (pour gérer les noms composés)
        parts = name.split('-')
        normalized_parts = []
        
        for part in parts:
            # Mettre la première lettre en majuscule et le reste en minuscules
            normalized_part = part.strip().capitalize()
            normalized_parts.append(normalized_part)
        
        # Rejoindre les parties avec un trait d'union
        return '-'.join(normalized_parts)

    def save(self, *args, **kwargs):
        """
        Surcharge de la méthode save pour normaliser les noms avant l'enregistrement
        """
        # Normaliser les noms et prénoms
        self.nom = self.normalize_name(self.nom)
        self.prenom = self.normalize_name(self.prenom)
        
        # Normaliser les noms d'artiste si présents
        if self.nom_artiste:
            self.nom_artiste = self.normalize_name(self.nom_artiste)
        if self.prenom_artiste:
            self.prenom_artiste = self.normalize_name(self.prenom_artiste)
        
        # Appeler la méthode save originale
        db.session.add(self)
        db.session.commit()

class Artwork(db.Model):
    __tablename__ = 'artworks'
    
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    numero = db.Column(db.String(50), unique=True)
    titre = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    technique = db.Column(db.String(200), default='')
    materiaux = db.Column(db.String(200), default='')
    annee_creation = db.Column(db.Integer)
    dimension_largeur = db.Column(db.Float)
    dimension_hauteur = db.Column(db.Float)
    dimension_profondeur = db.Column(db.Float)
    cadre_largeur = db.Column(db.Float)
    cadre_hauteur = db.Column(db.Float)
    cadre_profondeur = db.Column(db.Float)
    prix = db.Column(db.Float)
    photo_path = db.Column(db.String(200))
    model3d_path = db.Column(db.String(200))
    cube_3d_path = db.Column(db.String(500), nullable=True, default=None, comment='Chemin vers le cube 3D généré pour cette œuvre')
    qr_code_link = db.Column(db.String(200), default='', nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    statut = db.Column(db.String(20), default='en_attente')  # en_attente, selectionne, refuse
    
    # Colonnes de votes avec valeur par défaut explicite
    up_votes_count = db.Column(db.Integer, server_default='0', nullable=False)
    down_votes_count = db.Column(db.Integer, server_default='0', nullable=False)

    # Relation avec les votes
    votes = db.relationship('Vote', backref='artwork', lazy='dynamic')

    @property
    def total_votes(self):
        """Calcule le nombre total de votes pour cette œuvre."""
        return Vote.query.filter_by(artwork_id=self.id).count()

class Vote(db.Model):
    __tablename__ = 'votes'
    
    id = db.Column(db.Integer, primary_key=True)
    artwork_id = db.Column(db.Integer, db.ForeignKey('artworks.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vote_type = db.Column(db.String(10), nullable=False)
    vote_date = db.Column(db.DateTime, default=datetime.utcnow)

class Invitation(db.Model):
    __tablename__ = 'invitations'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'membre' ou 'artiste'
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)

    def is_expired(self):
        """Vérifie si l'invitation a expiré."""
        return datetime.utcnow() > self.expires_at

def create_admin_user(app):
    with app.app_context():
        admin = User.query.filter_by(email='admin@artcartel.com').first()
        if not admin:
            admin = User(
                username='admin_cartel',
                email='admin@artcartel.com', 
                is_admin=True
            )
            admin.set_password('AdminCartel2025!')
            db.session.add(admin)
            db.session.commit()
            logger.info("Utilisateur admin créé avec succès")

def create_test_users(app):
    with app.app_context():
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
        logger.info("Utilisateurs de test créés avec succès")
