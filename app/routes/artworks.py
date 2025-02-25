from flask import Blueprint, render_template, send_from_directory, current_app, request, jsonify, redirect, url_for, flash
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from app.models.models import db, Artwork, Vote, Artist
import os

bp = Blueprint('artworks', __name__, url_prefix='/artworks')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_upload_path():
    """Retourne le chemin du dossier d'upload."""
    return os.path.join(current_app.root_path, 'static', 'artworks')

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
        return jsonify({'error': 'Aucune image n\'a été fournie'}), 400
    
    file = request.files['photo']
    if file.filename == '':
        return jsonify({'error': 'Aucune image n\'a été sélectionnée'}), 400
        
    if not allowed_file(file.filename):
        return jsonify({'error': 'Format de fichier non autorisé. Utilisez JPG ou PNG.'}), 400

    # Sauvegarder l'image
    filename = secure_filename(file.filename)
    upload_dir = get_upload_path()
    os.makedirs(upload_dir, exist_ok=True)
    
    # Enregistrer le chemin relatif dans la base de données
    photo_path = os.path.join('artworks', filename)
    file.save(os.path.join(upload_dir, filename))

    # Créer l'œuvre dans la base de données
    artwork = Artwork(
        number=request.form['number'],
        name=request.form['name'],
        description=request.form.get('description', ''),
        technique=request.form['technique'],
        width=float(request.form['width']),
        height=float(request.form['height']),
        depth=float(request.form.get('depth', 0)) or None,
        price=float(request.form['price']),
        photo_path=photo_path,
        artist_id=current_user.artist.id
    )
    
    try:
        db.session.add(artwork)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur lors de la soumission'}), 500

@bp.route('/list')
@login_required
def list_artworks():
    artists = db.session.query(Artist.id, Artist.nom, Artist.prenom, Artist.nom_artiste)\
        .distinct()\
        .all()
    
    # Créer une liste d'artistes avec leurs œuvres
    artists_with_artworks = []
    for artist in artists:
        artworks = Artwork.query.filter_by(artist_id=artist[0]).all()
        artist_dict = {
            'id': artist[0],
            'nom': artist[1],
            'prenom': artist[2],
            'nom_artiste': artist[3],
            'artworks': artworks
        }
        artists_with_artworks.append(artist_dict)
    
    # Récupérer les votes de l'utilisateur et les compteurs
    user_votes = {}
    up_votes = {}
    down_votes = {}
    
    votes = Vote.query.all()
    for vote in votes:
        if vote.user_id == current_user.id:
            user_votes[vote.artwork_id] = vote.vote_type
        
        if vote.vote_type == 'up':
            up_votes[vote.artwork_id] = up_votes.get(vote.artwork_id, 0) + 1
        else:
            down_votes[vote.artwork_id] = down_votes.get(vote.artwork_id, 0) + 1
    
    return render_template('artworks/list.html', 
                         artists=artists_with_artworks,
                         user_votes=user_votes,
                         up_votes=up_votes,
                         down_votes=down_votes)

@bp.route('/vote/<int:artwork_id>', methods=['POST'])
@login_required
def vote(artwork_id):
    artwork = Artwork.query.get_or_404(artwork_id)
    vote_type = request.form.get('vote_type')
    
    if vote_type not in ['up', 'down']:
        flash('Type de vote invalide', 'error')
        return redirect(url_for('artworks.list_artworks'))
    
    existing_vote = Vote.query.filter_by(
        user_id=current_user.id,
        artwork_id=artwork_id
    ).first()
    
    if existing_vote:
        if existing_vote.vote_type == vote_type:
            # Si l'utilisateur vote dans le même sens, on supprime son vote
            db.session.delete(existing_vote)
            flash('Vote supprimé', 'success')
        else:
            # Si l'utilisateur change son vote, on met à jour le type
            existing_vote.vote_type = vote_type
            flash('Vote modifié', 'success')
    else:
        # Si pas de vote existant, on en crée un nouveau
        new_vote = Vote(
            user_id=current_user.id,
            artwork_id=artwork_id,
            vote_type=vote_type
        )
        db.session.add(new_vote)
        flash('Vote ajouté', 'success')
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash('Erreur lors du vote', 'error')
    
    return redirect(url_for('artworks.list_artworks'))

@bp.route('/get_votes/<int:artwork_id>')
@login_required
def get_votes(artwork_id):
    artwork = Artwork.query.get_or_404(artwork_id)
    
    # Compter les votes
    up_votes = Vote.query.filter_by(artwork_id=artwork_id, vote_type='up').count()
    down_votes = Vote.query.filter_by(artwork_id=artwork_id, vote_type='down').count()
    
    # Récupérer le vote de l'utilisateur courant
    user_vote = Vote.query.filter_by(
        user_id=current_user.id,
        artwork_id=artwork_id
    ).first()
    
    return jsonify({
        'up_votes': up_votes,
        'down_votes': down_votes,
        'user_vote': user_vote.vote_type if user_vote else None
    })

@bp.route('/selection/<int:artwork_id>/<action>', methods=['POST'])
@login_required
def selection(artwork_id, action):
    if not current_user.is_admin:
        flash('Permission refusée', 'error')
        return redirect(url_for('artworks.list_artworks'))
        
    artwork = Artwork.query.get_or_404(artwork_id)
    
    if action not in ['selectionne', 'refuse', 'en_attente']:
        flash('Action invalide', 'error')
        return redirect(url_for('artworks.list_artworks'))
        
    artwork.statut = action
    
    try:
        db.session.commit()
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
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@bp.route('/debug_images')
def debug_images():
    """Route de débogage pour afficher les informations des images."""
    artworks = Artwork.query.all()
    debug_info = []
    
    for artwork in artworks:
        artwork_info = {
            'name': artwork.name,
            'photo_path': artwork.photo_path,
            'url': url_for('static', filename=artwork.photo_path) if artwork.photo_path else None
        }
        
        if artwork.photo_path:
            full_path = os.path.join(current_app.root_path, 'app', 'static', artwork.photo_path)
            artwork_info.update({
                'full_path': full_path,
                'exists': os.path.exists(full_path),
                'static_folder': os.path.join(current_app.root_path, 'app', 'static'),
                'static_folder_exists': os.path.exists(os.path.join(current_app.root_path, 'app', 'static')),
                'uploads_folder_exists': os.path.exists(os.path.join(current_app.root_path, 'app', 'static', 'uploads')),
                'artworks_folder_exists': os.path.exists(os.path.join(current_app.root_path, 'app', 'static', 'uploads', 'artworks'))
            })
            
            if artwork_info['exists']:
                artwork_info['size'] = os.path.getsize(full_path)
                artwork_info['is_readable'] = os.access(full_path, os.R_OK)
    
    return jsonify({
        'artworks': debug_info,
        'static_url': url_for('static', filename='test.txt'),
        'app_root': current_app.root_path,
        'static_folder': current_app.static_folder
    })

@bp.route('/fix_image_paths')
@login_required
def fix_image_paths():
    """Corrige les chemins d'images dans la base de données."""
    artworks = Artwork.query.all()
    fixed_count = 0
    
    for artwork in artworks:
        if artwork.photo_path and 'uploads/artworks/' in artwork.photo_path:
            # Enlever 'uploads/' du chemin
            new_path = artwork.photo_path.replace('uploads/artworks/', 'artworks/')
            artwork.photo_path = new_path
            fixed_count += 1
    
    if fixed_count > 0:
        try:
            db.session.commit()
            flash(f'{fixed_count} chemins d\'images corrigés avec succès.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la correction des chemins : {str(e)}', 'danger')
    else:
        flash('Aucun chemin d\'image à corriger.', 'info')
    
    return redirect(url_for('artworks.list_artworks'))
