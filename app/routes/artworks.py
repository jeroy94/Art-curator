from flask import Blueprint, render_template, send_from_directory, current_app, request, jsonify, redirect, url_for, flash
from flask_login import current_user, login_required
from app.models.models import db, Artwork, Vote, Artist
import os

bp = Blueprint('artworks', __name__, url_prefix='/artworks')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/gallery')
def gallery():
    """Affiche la galerie d'œuvres."""
    artworks = Artwork.query.order_by(Artwork.created_at.desc()).all()
    return render_template('artworks/gallery.html', artworks=artworks)

@bp.route('/view/<int:artwork_id>')
def view(artwork_id):
    """Affiche une œuvre en détail avec son modèle 3D."""
    artwork = Artwork.query.get_or_404(artwork_id)
    return render_template('artworks/view.html', artwork=artwork)

@bp.route('/submit', methods=['GET', 'POST'])
@login_required
def submit():
    """Soumet une nouvelle œuvre."""
    if request.method == 'GET':
        return render_template('artworks/submit.html')
        
    if 'photo' not in request.files:
        flash('Aucune image n\'a été fournie', 'danger')
        return redirect(url_for('artworks.submit'))
    
    file = request.files['photo']
    if file.filename == '':
        flash('Aucune image n\'a été sélectionnée', 'danger')
        return redirect(url_for('artworks.submit'))
        
    if not allowed_file(file.filename):
        flash('Format de fichier non autorisé. Utilisez JPG ou PNG.', 'danger')
        return redirect(url_for('artworks.submit'))

    # Sauvegarder l'image
    filename = secure_filename(file.filename)
    photo_path = os.path.join('uploads', 'artworks', filename)
    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], 'artworks', filename))

    # Créer l'œuvre dans la base de données
    artwork = Artwork(
        numero=request.form['numero'],
        nom=request.form['nom'],
        description=request.form.get('description', ''),
        technique=request.form['technique'],
        dimension_largeur=float(request.form['dimension_largeur']),
        dimension_hauteur=float(request.form['dimension_hauteur']),
        dimension_profondeur=float(request.form.get('dimension_profondeur', 0)) or None,
        prix=float(request.form['prix']),
        photo_path=photo_path,
        artist_id=current_user.artist.id
    )
    
    try:
        db.session.add(artwork)
        db.session.commit()
        flash('Œuvre soumise avec succès !', 'success')
        return redirect(url_for('artworks.list_artworks'))
    except Exception as e:
        db.session.rollback()
        flash('Erreur lors de la soumission : ' + str(e), 'error')
        return redirect(url_for('artworks.submit'))

@bp.route('/list')
def list_artworks():
    """Affiche la liste des œuvres par artiste."""
    artists = Artist.query.all()
    
    # Récupérer les votes pour chaque œuvre
    up_votes = {}
    down_votes = {}
    user_votes = {}
    
    for artist in artists:
        for artwork in artist.artworks:
            # Debug: afficher les chemins des images
            if artwork.photo_path:
                print(f"Photo path pour {artwork.titre}: {artwork.photo_path}")
                print(f"Chemin complet: {os.path.join(current_app.root_path, 'static', artwork.photo_path)}")
            
            # Compter les votes positifs et négatifs
            up_count = Vote.query.filter_by(artwork_id=artwork.id, vote_type='up').count()
            down_count = Vote.query.filter_by(artwork_id=artwork.id, vote_type='down').count()
            up_votes[artwork.id] = up_count
            down_votes[artwork.id] = down_count
            
            # Si l'utilisateur est connecté, récupérer son vote
            if current_user.is_authenticated:
                user_vote = Vote.query.filter_by(
                    user_id=current_user.id,
                    artwork_id=artwork.id
                ).first()
                if user_vote:
                    user_votes[artwork.id] = user_vote.vote_type
    
    return render_template('artworks/list.html', 
                         artists=artists,
                         up_votes=up_votes,
                         down_votes=down_votes,
                         user_votes=user_votes)

@bp.route('/vote/<int:artwork_id>/<vote_type>', methods=['POST'])
@login_required
def vote(artwork_id, vote_type):
    if vote_type not in ['up', 'down']:
        flash('Type de vote invalide', 'error')
        return redirect(url_for('artworks.list_artworks'))
    
    artwork = Artwork.query.get_or_404(artwork_id)
    
    # Vérifier si l'utilisateur a déjà voté
    existing_vote = Vote.query.filter_by(
        user_id=current_user.id,
        artwork_id=artwork_id
    ).first()
    
    if existing_vote:
        if existing_vote.vote_type == vote_type:
            # Si même vote, on le supprime
            db.session.delete(existing_vote)
        else:
            # Si vote différent, on le met à jour
            existing_vote.vote_type = vote_type
    else:
        # Créer un nouveau vote
        new_vote = Vote(
            user_id=current_user.id,
            artwork_id=artwork_id,
            vote_type=vote_type
        )
        db.session.add(new_vote)
    
    try:
        db.session.commit()
        flash('Vote enregistré avec succès', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erreur lors de l\'enregistrement du vote', 'error')
    
    return redirect(url_for('artworks.list_artworks'))

@bp.route('/selection/<int:artwork_id>/<action>', methods=['POST'])
@login_required
def selection(artwork_id, action):
    if not current_user.is_admin:
        flash('Accès non autorisé', 'error')
        return redirect(url_for('artworks.list_artworks'))
    
    if action not in ['selectionne', 'refuse', 'en_attente']:
        flash('Action invalide', 'error')
        return redirect(url_for('artworks.list_artworks'))
    
    artwork = Artwork.query.get_or_404(artwork_id)
    old_status = artwork.statut
    artwork.statut = action
    
    try:
        db.session.commit()
        if action == 'en_attente':
            flash(f'L\'œuvre a été remise en attente', 'success')
        else:
            flash('Statut mis à jour avec succès', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erreur lors de la mise à jour du statut', 'error')
    
    return redirect(url_for('artworks.list_artworks'))

@bp.route('/selected')
def selected_artworks():
    """Affiche la liste des œuvres sélectionnées par artiste."""
    artists = Artist.query.join(Artist.artworks).filter(
        Artwork.statut == 'selectionne'
    ).distinct().order_by(Artist.nom.asc()).all()
    
    return render_template('artworks/selected.html', artists=artists)

@bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Sert les fichiers uploadés."""
    return send_from_directory(os.path.join(current_app.root_path, 'static'), filename)

@bp.route('/get_votes/<int:artwork_id>')
def get_votes(artwork_id):
    """Obtenir le nombre de votes pour une œuvre."""
    up_votes = Vote.query.filter_by(artwork_id=artwork_id, vote_type='up').count()
    down_votes = Vote.query.filter_by(artwork_id=artwork_id, vote_type='down').count()
    
    # Obtenir le vote de l'utilisateur connecté
    user_vote = None
    if current_user.is_authenticated:
        vote = Vote.query.filter_by(
            artwork_id=artwork_id,
            user_id=current_user.id
        ).first()
        if vote:
            user_vote = vote.vote_type
    
    return jsonify({
        'up_votes': up_votes,
        'down_votes': down_votes,
        'user_vote': user_vote
    })
