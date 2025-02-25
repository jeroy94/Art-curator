"""
Routes principales de l'application.
"""
from flask import Blueprint, render_template
from ..models.models import Artwork

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Page d'accueil."""
    recent_artworks = Artwork.query.order_by(Artwork.created_at.desc()).limit(6).all()
    return render_template('index.html', recent_artworks=recent_artworks)
