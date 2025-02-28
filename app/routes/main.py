"""
Routes principales de l'application.
"""
from flask import Blueprint, render_template, current_app
from ..models.models import Artwork
import logging

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Page d'accueil."""
    recent_artworks = Artwork.query.order_by(Artwork.created_at.desc()).limit(6).all()
    return render_template('index.html', recent_artworks=recent_artworks)

@bp.route('/debug_routes')
def debug_routes():
    """Route de débogage pour lister toutes les routes."""
    routes = []
    for rule in current_app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'route': str(rule)
        })
    
    # Log des routes
    logger = logging.getLogger(__name__)
    logger.info("Routes disponibles :")
    for route in routes:
        logger.info(f"Endpoint: {route['endpoint']}")
        logger.info(f"  Méthodes : {route['methods']}")
        logger.info(f"  Chemin : {route['route']}")
    
    return render_template('debug_routes.html', routes=routes)
