from flask import Blueprint, jsonify, request, current_app, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.models import Artist, Artwork, db, Vote, User
from functools import wraps

bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Accès administrateur requis', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Page d'administration principale."""
    artists = Artist.query.all()
    artworks = Artwork.query.all()
    users = User.query.all()
    return render_template('admin/dashboard.html', 
                         artists=artists, 
                         artworks=artworks, 
                         users=users)

@bp.route('/artists')
@login_required
@admin_required
def list_artists():
    """Liste tous les artistes."""
    artists = Artist.query.all()
    return render_template('admin/artists.html', artists=artists)

@bp.route('/artworks')
@login_required
@admin_required
def list_artworks():
    """Liste toutes les œuvres."""
    artworks = Artwork.query.all()
    return render_template('admin/artworks.html', artworks=artworks)

@bp.route('/artwork/<int:artwork_id>/selection', methods=['POST'])
@login_required
@admin_required
def update_artwork_selection(artwork_id):
    """Met à jour le statut de sélection d'une œuvre."""
    artwork = Artwork.query.get_or_404(artwork_id)
    artwork.status = 'selected' if request.form.get('selected') == 'true' else 'pending'
    db.session.commit()
    flash('Statut de l\'œuvre mis à jour', 'success')
    return redirect(url_for('admin.list_artworks'))

@bp.route('/statistics')
@login_required
@admin_required
def get_statistics():
    """Affiche les statistiques."""
    stats = {
        'total_artists': Artist.query.count(),
        'total_artworks': Artwork.query.count(),
        'selected_artworks': Artwork.query.filter_by(status='selected').count(),
        'total_users': User.query.count()
    }
    return render_template('admin/statistics.html', stats=stats)

@bp.route('/generate-pdfs')
@login_required
@admin_required
def generate_pdfs():
    """Génère les PDF pour les artistes sélectionnés."""
    # Logique de génération des PDF à implémenter
    flash('Génération des PDF en cours...', 'info')
    return redirect(url_for('admin.dashboard'))
