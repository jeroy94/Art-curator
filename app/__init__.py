from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from app.models.models import db, init_db, User
import os
import secrets

def create_app():
    app = Flask(__name__)
    
    # Config
    from config import Config
    app.config.from_object(Config)
    
    # Configuration de la session
    app.config['SECRET_KEY'] = secrets.token_hex(32)  # Générer une clé secrète sécurisée
    app.config['SESSION_TYPE'] = 'filesystem'  # Stockage des sessions sur le système de fichiers
    app.config['SESSION_PERMANENT'] = False  # Sessions non permanentes
    app.config['SESSION_USE_SIGNER'] = True  # Signer les sessions
    
    # Initialize extensions
    init_db(app)
    Migrate(app, db)
    CORS(app)
    JWTManager(app)
    
    # Initialiser la session
    from flask_session import Session
    Session(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Create upload folder if it doesn't exist
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # Configuration du logger pour la compatibilité Windows
    import sys
    import logging
    import io

    # Créer un gestionnaire de flux qui gère l'encodage UTF-8
    class UTF8StreamHandler(logging.StreamHandler):
        def __init__(self, stream=None):
            if stream is None:
                stream = sys.stdout
            super().__init__(stream)

        def format(self, record):
            # Convertir les emojis et caractères spéciaux en leur représentation textuelle
            msg = super().format(record)
            return msg.encode('ascii', 'ignore').decode('ascii')

    # Configuration du logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            UTF8StreamHandler(),  # Gestionnaire de flux personnalisé
            logging.FileHandler('app.log', encoding='utf-8')  # Fichier log en UTF-8
        ]
    )

    # Rediriger stdout vers un flux qui gère l'encodage
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    # Register blueprints
    from app.routes import auth, artists, admin, artworks, test
    app.register_blueprint(auth.bp)
    app.register_blueprint(artists.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(artworks.bp)
    app.register_blueprint(test.bp)
    
    # Jinja2 filters
    @app.template_filter('selectonly')
    def selectonly_filter(artworks):
        """Filtre qui retourne True si l'artiste a au moins une œuvre sélectionnée."""
        return any(artwork.statut == 'selectionne' for artwork in artworks)
    
    return app
