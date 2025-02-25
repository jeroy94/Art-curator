from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from app.models.models import db, init_db, User

def create_app():
    app = Flask(__name__)
    
    # Config
    from config import Config
    app.config.from_object(Config)
    
    # Initialize extensions
    init_db(app)
    Migrate(app, db)
    CORS(app)
    JWTManager(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Create upload folder if it doesn't exist
    import os
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
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
