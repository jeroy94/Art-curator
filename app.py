from flask import Flask, send_from_directory, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_mail import Mail
from flask_session import Session
from app.models.models import db, User
import os
import secrets

def create_app():
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(__file__), 'app', 'templates'),
                static_folder=os.path.join(os.path.dirname(__file__), 'app', 'static'))
    
    # Configuration
    app.config.from_object('config.Config')
    
    # Configuration de la session
    app.config['SECRET_KEY'] = secrets.token_hex(32)
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = os.path.join(os.path.dirname(__file__), 'flask_session')
    
    # Créer le dossier pour les sessions si nécessaire
    os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)
    
    # Ensure the upload folders exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'input'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'output'), exist_ok=True)
    
    # Initialize extensions
    CORS(app)
    db.init_app(app)
    jwt = JWTManager(app)
    mail = Mail(app)
    Session(app)  # Initialiser la session Flask
    
    # Configure Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Import blueprints
    from app.routes import auth, artworks, admin, processing, main, artists
    
    # Register blueprints for API routes
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp, url_prefix='/auth')
    app.register_blueprint(artworks.bp, url_prefix='/artworks')
    app.register_blueprint(admin.bp, url_prefix='/admin')
    app.register_blueprint(artists.bp, url_prefix='/artists')
    app.register_blueprint(processing.bp, url_prefix='/processing')
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create admin user if it doesn't exist
        admin_user = User.query.filter_by(email='admin@example.com').first()
        if not admin_user:
            admin_user = User(
                email='admin@example.com',
                username='admin',
                is_admin=True
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()

    return app

if __name__ == '__main__':
    app = create_app()
    print("🚀 Application démarrée en mode debug")
    print("Enregistrement des routes :")
    for rule in app.url_map.iter_rules():
        print(f" - {rule.endpoint}: {rule}")
    app.run(debug=True, host='0.0.0.0', port=5000)
