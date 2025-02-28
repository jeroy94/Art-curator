from flask import Flask
from flask_mail import Mail

mail = Mail()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    from config import Config
    app.config.from_object(Config)
    
    # Initialiser les extensions
    mail.init_app(app)
    
    # Import blueprints
    from app.routes import auth, artists, admin, artworks, test, processing, main
    
    # Débogage des blueprints
    import logging
    import sys
    
    # Configuration du logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('app_debug.log')
        ]
    )
    logger = logging.getLogger(__name__)
    
    logger.info("Enregistrement des blueprints...")
    logger.info(f"main: {main.bp}")
    logger.info(f"auth: {auth.bp}")
    logger.info(f"artists: {artists.bp}")
    logger.info(f"artworks: {artworks.bp}")
    logger.info(f"test: {test.bp}")
    logger.info(f"processing: {processing.bp}")
    logger.info(f"admin: {admin.admin_bp}")
    
    # Register blueprints
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp, url_prefix='/auth')
    app.register_blueprint(artists.bp, url_prefix='/artists')
    app.register_blueprint(artworks.bp, url_prefix='/artworks')
    app.register_blueprint(test.bp, url_prefix='/test')
    app.register_blueprint(processing.bp, url_prefix='/processing')
    app.register_blueprint(admin.admin_bp, url_prefix='/admin')
    
    # Lister toutes les routes
    logger.info("Routes disponibles :")
    for rule in app.url_map.iter_rules():
        logger.info(f"Endpoint: {rule.endpoint}")
        logger.info(f"  Méthodes : {rule.methods}")
        logger.info(f"  Chemin : {rule}")
        
        # Essayer de trouver la fonction associée
        try:
            func = app.view_functions.get(rule.endpoint)
            if func:
                logger.info(f"  Fonction : {func.__name__}")
                logger.info(f"  Module : {func.__module__}")
            else:
                logger.warning(f"  Aucune fonction trouvée pour {rule.endpoint}")
        except Exception as e:
            logger.error(f"  Erreur lors de la récupération de la fonction : {e}")
    
    # Configuration du logger de l'application
    app.logger.setLevel(logging.DEBUG)
    
    return app
