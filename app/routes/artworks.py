from flask import Blueprint, render_template, send_from_directory, current_app, request, jsonify, redirect, url_for, flash, session
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from app.models.models import db, Artwork, Vote, Artist
import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from flask import send_file
import io
from PIL import Image as PILImage

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

@bp.route('/vote/<int:artwork_id>', methods=['POST'])
@login_required
def vote(artwork_id):
    # Vérifier si c'est une requête AJAX
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        current_app.logger.warning(f'Vote attempt without AJAX: {request.headers}')
        return jsonify({'status': 'error', 'message': 'Requête non autorisée'}), 403

    # Log de débogage
    current_app.logger.info(f'Vote received for artwork {artwork_id} by user {current_user.id}')
    current_app.logger.info(f'Vote type: {request.form.get("vote_type")}')

    # Stocker temporairement le vote en session
    session['temp_vote'] = {
        'artwork_id': artwork_id,
        'vote_type': request.form.get('vote_type')
    }

    return jsonify({
        'status': 'success',
        'message': 'Vote en attente de validation'
    })

@bp.route('/validate_vote', methods=['POST'])
@login_required
def validate_vote():
    # Vérifier si c'est une requête AJAX
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        current_app.logger.warning(f'Vote validation attempt without AJAX: {request.headers}')
        return jsonify({'status': 'error', 'message': 'Requête non autorisée'}), 403

    # Log de débogage
    current_app.logger.info(f'Vote validation for user {current_user.id}')

    # Récupérer le vote temporaire depuis la session
    temp_vote = session.get('temp_vote')
    if not temp_vote:
        current_app.logger.warning(f'No temporary vote found for user {current_user.id}')
        return jsonify({'status': 'error', 'message': 'Aucun vote en attente'}), 400

    artwork_id = temp_vote['artwork_id']
    vote_type = temp_vote['vote_type']
    artwork = Artwork.query.get_or_404(artwork_id)

    # Log de débogage
    current_app.logger.info(f'Processing vote for artwork {artwork_id}, type: {vote_type}')

    # Récupérer le vote de l'utilisateur courant
    user_vote = Vote.query.filter_by(
        user_id=current_user.id, 
        artwork_id=artwork_id
    ).first()

    if user_vote:
        if user_vote.vote_type == vote_type:
            # L'utilisateur annule son vote
            current_app.logger.info(f'User {current_user.id} cancelling vote for artwork {artwork_id}')
            db.session.delete(user_vote)
        else:
            # L'utilisateur change son vote
            current_app.logger.info(f'User {current_user.id} changing vote for artwork {artwork_id}')
            user_vote.vote_type = vote_type
    else:
        # Nouveau vote
        current_app.logger.info(f'User {current_user.id} creating new vote for artwork {artwork_id}')
        new_vote = Vote(
            user_id=current_user.id,
            artwork_id=artwork_id,
            vote_type=vote_type
        )
        db.session.add(new_vote)

    db.session.commit()

    # Effacer le vote temporaire de la session
    session.pop('temp_vote', None)

    # Récupérer les nouveaux compteurs de votes
    up_votes = Vote.query.filter_by(artwork_id=artwork_id, vote_type='up').count()
    down_votes = Vote.query.filter_by(artwork_id=artwork_id, vote_type='down').count()

    current_app.logger.info(f'Vote counts for artwork {artwork_id}: up={up_votes}, down={down_votes}')

    return jsonify({
        'status': 'success',
        'up_votes': up_votes,
        'down_votes': down_votes
    })

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
        return jsonify({'success': False, 'message': 'Permission refusée'}), 403
        
    artwork = Artwork.query.get_or_404(artwork_id)
    
    if action not in ['selectionne', 'refuse', 'en_attente']:
        return jsonify({'success': False, 'message': 'Action invalide'}), 400
        
    artwork.statut = action
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Statut mis à jour avec succès'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Erreur lors de la mise à jour du statut'}), 500

@bp.route('/selected_artworks')
@login_required
def selected_artworks():
    """Affiche la liste des œuvres sélectionnées par artiste."""
    # Récupérer tous les artistes avec leurs œuvres sélectionnées
    artists = Artist.query.join(Artwork).filter(Artwork.statut == 'selectionne').order_by(Artist.nom).all()
    
    # Filtrer les artistes pour ne garder que ceux avec des œuvres sélectionnées
    artists_with_selected = [
        artist for artist in artists 
        if any(artwork.statut == 'selectionne' for artwork in artist.artworks)
    ]
    
    return render_template('artworks/selected_artworks.html', artists=artists_with_selected)

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
    
    return redirect(url_for('artworks.selected_artworks'))

@bp.route('/validate_all_votes', methods=['POST'])
@login_required
def validate_all_votes():
    # Vérifier si c'est une requête AJAX
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        current_app.logger.warning(f'All votes validation attempt without AJAX: {request.headers}')
        return jsonify({'status': 'error', 'message': 'Requête non autorisée'}), 403

    # Log de débogage
    current_app.logger.info(f'Validating all votes for user {current_user.id}')

    # Récupérer toutes les œuvres
    artworks = Artwork.query.all()
    up_votes_count = {}
    down_votes_count = {}

    for artwork in artworks:
        # Récupérer le vote de l'utilisateur courant pour cette œuvre
        user_vote = Vote.query.filter_by(
            user_id=current_user.id, 
            artwork_id=artwork.id
        ).first()

        # Supprimer le vote existant s'il existe
        if user_vote:
            current_app.logger.info(f'Removing existing vote for artwork {artwork.id}')
            db.session.delete(user_vote)

        # Récupérer les votes temporaires de la session
        temp_vote = session.get(f'temp_vote_{artwork.id}')
        if temp_vote:
            current_app.logger.info(f'Processing temporary vote for artwork {artwork.id}')
            new_vote = Vote(
                user_id=current_user.id,
                artwork_id=artwork.id,
                vote_type=temp_vote['vote_type']
            )
            db.session.add(new_vote)
            # Supprimer le vote temporaire de la session
            session.pop(f'temp_vote_{artwork.id}', None)

        # Compter les votes
        up_votes_count[artwork.id] = Vote.query.filter_by(artwork_id=artwork.id, vote_type='up').count()
        
        down_votes_count[artwork.id] = Vote.query.filter_by(artwork_id=artwork.id, vote_type='down').count()

    # Valider toutes les modifications
    db.session.commit()

    current_app.logger.info('All votes validated successfully')

    return jsonify({
        'status': 'success',
        'up_votes': up_votes_count,
        'down_votes': down_votes_count
    })

@bp.route('/validate_votes', methods=['POST'])
@login_required
def validate_votes():
    # Vérifier si c'est une requête AJAX
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        current_app.logger.warning(f'Votes validation attempt without AJAX: {request.headers}')
        return jsonify({'status': 'error', 'message': 'Requête non autorisée'}), 403

    # Log de débogage
    current_app.logger.info(f'Validating votes for user {current_user.id}')

    # Récupérer les votes à valider
    votes = request.form.to_dict()
    up_votes_count = {}
    down_votes_count = {}

    for artwork_id_str, vote_type in votes.items():
        try:
            artwork_id = int(artwork_id_str)
        except ValueError:
            current_app.logger.warning(f'Invalid artwork ID: {artwork_id_str}')
            continue

        # Vérifier que l'œuvre existe
        artwork = Artwork.query.get(artwork_id)
        if not artwork:
            current_app.logger.warning(f'Artwork not found: {artwork_id}')
            continue

        # Récupérer le vote existant de l'utilisateur
        user_vote = Vote.query.filter_by(
            user_id=current_user.id, 
            artwork_id=artwork_id
        ).first()

        # Supprimer le vote existant s'il existe
        if user_vote:
            current_app.logger.info(f'Removing existing vote for artwork {artwork_id}')
            db.session.delete(user_vote)

        # Créer un nouveau vote
        new_vote = Vote(
            user_id=current_user.id,
            artwork_id=artwork_id,
            vote_type=vote_type
        )
        db.session.add(new_vote)

        # Compter les votes
        up_votes_count[artwork_id] = Vote.query.filter_by(artwork_id=artwork_id, vote_type='up').count()
        
        down_votes_count[artwork_id] = Vote.query.filter_by(artwork_id=artwork_id, vote_type='down').count()

    # Valider toutes les modifications
    db.session.commit()

    current_app.logger.info('Votes validated successfully')

    return jsonify({
        'status': 'success',
        'up_votes': up_votes_count,
        'down_votes': down_votes_count
    })

@bp.route('/submit_vote', methods=['POST'])
@login_required
def submit_vote():
    """Soumettre des votes pour plusieurs œuvres depuis le salon de vote."""
    # Récupérer tous les votes du formulaire
    votes = {}
    for key, value in request.form.items():
        if key.startswith('vote_'):
            artwork_id = key.split('_')[1]
            votes[artwork_id] = value

    # Dictionnaires pour stocker les résultats
    up_votes_count = {}
    down_votes_count = {}

    # Traiter chaque vote
    for artwork_id_str, vote_value in votes.items():
        try:
            artwork_id = int(artwork_id_str)
        except ValueError:
            current_app.logger.warning(f'Invalid artwork ID: {artwork_id_str}')
            continue

        # Vérifier que l'œuvre existe
        artwork = Artwork.query.get(artwork_id)
        if not artwork:
            current_app.logger.warning(f'Artwork not found: {artwork_id}')
            continue

        # Supprimer le vote existant de l'utilisateur pour cette œuvre
        existing_vote = Vote.query.filter_by(
            user_id=current_user.id, 
            artwork_id=artwork_id
        ).first()

        if existing_vote:
            current_app.logger.info(f'Removing existing vote for artwork {artwork_id}')
            db.session.delete(existing_vote)

        # Créer un nouveau vote
        new_vote = Vote(
            user_id=current_user.id,
            artwork_id=artwork_id,
            vote_type=vote_value
        )
        db.session.add(new_vote)

        # Compter les votes pour cette œuvre
        up_votes_count[artwork_id] = Vote.query.filter_by(artwork_id=artwork_id, vote_type='up').count()
        
        down_votes_count[artwork_id] = Vote.query.filter_by(artwork_id=artwork_id, vote_type='down').count()

    # Valider toutes les modifications
    db.session.commit()

    current_app.logger.info('Votes validated successfully')

    return jsonify({
        'status': 'success',
        'up_votes': up_votes_count,
        'down_votes': down_votes_count
    })

@bp.route('/salon_de_vote', methods=['GET', 'POST'])
@login_required
def salon_de_vote():
    # Vérification explicite de la requête AJAX
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.method == 'POST':
        try:
            # Log détaillé des en-têtes et du formulaire
            current_app.logger.info(f"Requête reçue - Méthode : {request.method}")
            current_app.logger.info(f"Headers : {dict(request.headers)}")
            current_app.logger.info(f"Arguments : {request.args}")
            current_app.logger.info(f"Formulaire : {request.form}")
            current_app.logger.info(f"Requête AJAX : {is_ajax}")

            action = request.form.get('action')
            current_app.logger.info(f"Action reçue : {action}")

            if action == 'vote':
                votes = {}
                for key, value in request.form.items():
                    if key.startswith('vote_'):
                        artwork_id = key.split('_')[1]
                        votes[artwork_id] = value
                
                current_app.logger.info(f"Votes reçus : {votes}")
                
                for artwork_id, vote_value in votes.items():
                    current_app.logger.info(f"Mise à jour du vote pour l'œuvre {artwork_id} ")
                    update_artwork_vote(artwork_id, vote_value, current_user)

            elif action == 'selection' and current_user.is_admin:
                selections = {}
                for key, value in request.form.items():
                    if key.startswith('selection_'):
                        artwork_id = key.split('_')[1]
                        selections[artwork_id] = value
                
                current_app.logger.info(f"Sélections reçues : {selections}")
                
                selected_artworks = [int(k.split('_')[1]) for k, v in request.form.items() 
                                     if k.startswith('selection_') and v == 'selectionne']
                refused_artworks = [int(k.split('_')[1]) for k, v in request.form.items() 
                                    if k.startswith('selection_') and v == 'refuse']
                
                current_app.logger.info(f"Sélections validées : {selected_artworks}, {refused_artworks}")
                
                update_artwork_selections(selected_artworks, refused_artworks)

            # Réponse différente selon le type de requête
            if is_ajax:
                return jsonify({
                    'status': 'success', 
                    'message': 'Votes et sélections mis à jour avec succès'
                }), 200
            else:
                return redirect(url_for('artworks.salon_de_vote'))

        except Exception as e:
            current_app.logger.error(f"Erreur lors du traitement : {str(e)}")
            if is_ajax:
                return jsonify({
                    'status': 'error', 
                    'message': 'Une erreur est survenue lors du traitement'
                }), 500
            else:
                flash('Une erreur est survenue', 'danger')
                return redirect(url_for('artworks.salon_de_vote'))

    return render_template('artworks/salon_de_vote.html', 
                           artistes_data=get_artistes_data(), 
                           user_votes=get_user_votes(current_user),
                           user_selections=get_user_selections())

@bp.route('/validate_selections', methods=['POST'])
@login_required
def validate_selections():
    # Vérifier si c'est une requête AJAX
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        current_app.logger.warning(f'Selections validation attempt without AJAX: {request.headers}')
        return jsonify({'status': 'error', 'message': 'Requête non autorisée'}), 403

    # Vérifier les permissions (seulement les administrateurs)
    if not current_user.is_admin:
        current_app.logger.warning(f'Non-admin user {current_user.id} attempted to validate selections')
        return jsonify({'status': 'error', 'message': 'Permission refusée'}), 403

    # Log de débogage
    current_app.logger.info(f'Validating selections for user {current_user.id}')

    # Récupérer toutes les œuvres
    artworks = Artwork.query.all()
    selected_artworks = []
    refused_artworks = []

    for artwork in artworks:
        # Chercher les champs de sélection avec le bon préfixe
        selection_status = request.form.get(f'selection_{artwork.id}')
        
        current_app.logger.info(f'Artwork {artwork.id} selection status: {selection_status}')
        
        if selection_status == 'selectionner':
            artwork.statut = 'selectionne'
            selected_artworks.append(artwork.id)
        elif selection_status == 'refuser':
            artwork.statut = 'refuse'
            refused_artworks.append(artwork.id)
        else:
            artwork.statut = 'en_attente'

    try:
        db.session.commit()
        current_app.logger.info('Selections validated successfully')
        
        return jsonify({
            'status': 'success',
            'action': 'selection',
            'selected_artworks': selected_artworks,
            'refused_artworks': refused_artworks
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error validating selections: {str(e)}')
        return jsonify({
            'status': 'error', 
            'message': 'Erreur lors de la validation des sélections'
        }), 500

def get_artistes_data():
    """
    Récupère les données des artistes avec leurs œuvres.
    
    Returns:
        list: Liste des groupes d'artistes avec leurs œuvres
    """
    artistes_data = []
    artists = Artist.query.all()
    
    for artist in artists:
        artworks = Artwork.query.filter_by(artist_id=artist.id).all()
        artiste_groupe = {
            'nom': artist.nom,
            'artworks': artworks
        }
        artistes_data.append(artiste_groupe)
    
    return artistes_data

def get_user_votes(current_user):
    """
    Récupère les votes de l'utilisateur actuel.
    
    Args:
        current_user: Utilisateur connecté
    
    Returns:
        dict: Dictionnaire des votes de l'utilisateur
    """
    user_votes = {}
    if current_user.is_authenticated:
        existing_votes = Vote.query.filter_by(user_id=current_user.id).all()
        user_votes = {str(vote.artwork_id): vote.vote_type for vote in existing_votes}
    
    return user_votes

def get_user_selections():
    """
    Récupère les sélections des œuvres.
    
    Returns:
        dict: Dictionnaire des statuts des œuvres
    """
    user_selections = {str(artwork.id): artwork.statut for artwork in Artwork.query.all() 
                       if artwork.statut in ['selectionne', 'refuse']}
    
    return user_selections

def update_artwork_vote(artwork_id, vote_type, current_user):
    """
    Met à jour le vote pour une œuvre.
    
    Args:
        artwork_id (int): ID de l'œuvre
        vote_type (str): Type de vote ('up' ou 'down')
        current_user: Utilisateur connecté
    """
    existing_vote = Vote.query.filter_by(
        artwork_id=artwork_id, 
        user_id=current_user.id
    ).first()
    
    if existing_vote:
        current_app.logger.info(f'Mise à jour du vote pour l\'œuvre {artwork_id}')
        existing_vote.vote_type = vote_type
    else:
        current_app.logger.info(f'Nouveau vote pour l\'œuvre {artwork_id}')
        new_vote = Vote(
            artwork_id=artwork_id, 
            user_id=current_user.id, 
            vote_type=vote_type
        )
        db.session.add(new_vote)
    
    db.session.commit()

def update_artwork_selections(selected_artworks, refused_artworks):
    """
    Met à jour les sélections des œuvres.
    
    Args:
        selected_artworks (list): Liste des IDs des œuvres sélectionnées
        refused_artworks (list): Liste des IDs des œuvres refusées
    """
    for artwork_id in selected_artworks:
        artwork = Artwork.query.get(artwork_id)
        if artwork:
            artwork.statut = 'selectionne'
    
    for artwork_id in refused_artworks:
        artwork = Artwork.query.get(artwork_id)
        if artwork:
            artwork.statut = 'refuse'
    
    db.session.commit()

def resize_image_for_pdf(image_path, max_height_mm=20):
    """Redimensionne une image pour l'export PDF en préservant ses proportions."""
    try:
        # Ouvrir l'image
        img = PILImage.open(image_path)
        
        # Convertir mm en pixels (approximatif, 1 mm ≈ 3.78 pixels)
        max_height_px = int(max_height_mm * 3.78)
        
        # Calculer le ratio de redimensionnement
        width, height = img.size
        
        # Si l'image est plus petite que la hauteur maximale, ne pas redimensionner
        if height <= max_height_px:
            return img
        
        # Calculer la nouvelle largeur proportionnellement
        ratio = max_height_px / height
        new_width = int(width * ratio)
        
        # Redimensionner l'image avec une méthode de haute qualité
        img_resized = img.resize((new_width, max_height_px), PILImage.LANCZOS)
        
        current_app.logger.info(f"Image originale: {width}x{height}")
        current_app.logger.info(f"Image redimensionnée: {new_width}x{max_height_px}")
        
        return img_resized
    except Exception as e:
        current_app.logger.error(f"Erreur de redimensionnement: {e}")
        return None

@bp.route('/export_selected_artworks_pdf')
@login_required
def export_selected_artworks_pdf():
    """Exporter les œuvres sélectionnées en PDF."""
    try:
        # Récupérer les artistes avec leurs œuvres sélectionnées
        artists = Artist.query.join(Artwork).filter(Artwork.statut == 'selectionne').order_by(Artist.nom).all()
        
        # Préparer le buffer PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        
        # Style personnalisé pour les titres et le contenu
        title_style = ParagraphStyle(
            'TitleStyle', 
            parent=styles['Heading1'], 
            textColor=colors.black
        )
        artist_style = ParagraphStyle(
            'ArtistStyle', 
            parent=styles['Heading2'], 
            textColor=colors.black,
            leftIndent=-20*mm  # Décalage de 20mm vers la droite
        )
        normal_style = ParagraphStyle(
            'NormalBlack', 
            parent=styles['Normal'], 
            textColor=colors.black
        )
        
        # Style pour le prix (également en noir)
        price_style = ParagraphStyle(
            'PriceStyle', 
            parent=normal_style, 
            alignment=2,  # Alignement à droite
            textColor=colors.black
        )
        
        # Contenu du PDF
        story = []
        
        # Titre principal
        story.append(Paragraph("Catalogue des Œuvres Sélectionnées", title_style))
        story.append(Spacer(1, 12))
        
        for artist in artists:
            # Nom de l'artiste
            artist_name = artist.nom_artiste or f"{artist.prenom} {artist.nom}"
            if artist.nom_artiste:
                artist_name += f" ({artist.nom_artiste})"
            artist_paragraph = Paragraph(artist_name, artist_style)
            story.append(artist_paragraph)
            story.append(Spacer(1, 6))
            
            for artwork in artist.artworks:
                if artwork.statut == 'selectionne':
                    # Description des dimensions
                    dimensions_parts = []
                    for dim_name in ['dimension_largeur', 'dimension_hauteur', 'dimension_profondeur']:
                        dim = getattr(artwork, dim_name)
                        if dim is not None:
                            dimensions_parts.append(str(int(dim)))

                    dimensions_str = 'x'.join(dimensions_parts) + ' cm' if dimensions_parts else 'Non renseignées'
                    
                    # Gérer l'image de l'œuvre
                    artwork_img = Paragraph("Aucune image", normal_style)
                    
                    # Vérifier si le chemin de la photo est défini et non vide
                    if artwork.photo_path and artwork.photo_path.strip():
                        # Extraire le nom de fichier, en supprimant le préfixe 'artworks/' si présent
                        photo_filename = artwork.photo_path.strip().split('/')[-1]
                        
                        # Chemins possibles de l'image
                        possible_paths = [
                            os.path.join(current_app.root_path, 'app', 'static', artwork.photo_path),
                            os.path.join(current_app.root_path, 'app', 'static', 'artworks', photo_filename),
                            os.path.join(current_app.root_path, 'static', 'artworks', photo_filename),
                            os.path.join(current_app.root_path, 'static', artwork.photo_path)
                        ]
                        
                        img_path = None
                        for path in possible_paths:
                            if os.path.exists(path):
                                img_path = path
                                break
                        
                        if img_path:
                            try:
                                # Redimensionner l'image
                                pil_img = resize_image_for_pdf(img_path)
                                
                                if pil_img:
                                    # Sauvegarder l'image temporairement
                                    temp_image_path = os.path.join(current_app.root_path, 'static', f'temp_artwork_{artwork.id}.png')
                                    pil_img.save(temp_image_path)
                                    
                                    # Calculer la largeur proportionnelle
                                    img_width = pil_img.width
                                    img_height = pil_img.height
                                    
                                    # Créer l'image pour ReportLab
                                    artwork_img = Image(temp_image_path, width=img_width*mm/3.78, height=img_height*mm/3.78)
                                else:
                                    artwork_img = Paragraph("Image non disponible", normal_style)
                            except Exception as e:
                                current_app.logger.error(f"Erreur lors du traitement de l'image: {e}")
                                artwork_img = Paragraph(f"Erreur de traitement: {e}", normal_style)
                    
                    # Créer un tableau pour chaque œuvre
                    table_data = [
                        [artwork_img, Paragraph(f"""
                            <b>Titre :</b> {artwork.titre}<br/>
                            <b>Technique :</b> {artwork.technique}<br/>
                            <b>Dimensions :</b> {dimensions_str}
                        """, normal_style), 
                        Paragraph(f"""
                            <b>Prix :</b> {artwork.prix} € {"" if artwork.prix else "Non défini"}
                        """, price_style)]
                    ]
                    
                    # Largeur totale de la page A4
                    page_width = 210 * mm
                    
                    table = Table(table_data, 
                        colWidths=[30*mm, 130*mm, 40*mm],  # Image, détails, prix
                        rowHeights=[60]  # Hauteur à 60mm
                    )
                    table.setStyle(TableStyle([
                        ('ALIGN', (0,0), (0,0), 'LEFT'),     # Image alignée à gauche
                        ('ALIGN', (2,0), (2,0), 'RIGHT'),    # Prix aligné à droite
                        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                        ('GRID', (0,0), (-1,-1), 1, colors.black),
                        ('BACKGROUND', (0,0), (-1,0), colors.beige)
                    ]))
                    
                    story.append(table)
        
        # Construire le PDF
        doc.build(story)
        
        # Réinitialiser le buffer
        buffer.seek(0)
        
        # Renvoyer le PDF
        return send_file(
            buffer, 
            download_name='Catalogue_Artworks.pdf', 
            as_attachment=True, 
            mimetype='application/pdf'
        )
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la génération du PDF: {e}")
        flash("Une erreur est survenue lors de la génération du PDF.", "error")
        return redirect(url_for('main.index'))

@bp.route('/export_selected_pdf', methods=['GET'])
@login_required
def export_selected_pdf():
    """Exporte les œuvres sélectionnées en PDF."""
    # Récupérer tous les artistes avec leurs œuvres sélectionnées
    artists = Artist.query.join(Artwork).filter(Artwork.statut == 'selectionne').order_by(Artist.nom).all()
    
    # Créer un buffer en mémoire pour le PDF
    buffer = io.BytesIO()
    
    # Créer le document PDF
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    # Styles pour le PDF
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    normal_style = styles['Normal']
    
    # Éléments à ajouter au PDF
    elements = []
    
    # Titre du document
    elements.append(Paragraph("Œuvres Sélectionnées", title_style))
    elements.append(Spacer(1, 12))
    
    # Parcourir les artistes et leurs œuvres
    for artist in artists:
        selected_artworks = [artwork for artwork in artist.artworks if artwork.statut == 'selectionne']
        
        if selected_artworks:
            # Nom de l'artiste
            artist_name = f"{artist.nom} {artist.prenom}"
            if artist.nom_artiste:
                artist_name += f" ({artist.nom_artiste})"
            artist_style = ParagraphStyle(
                'ArtistStyle', 
                parent=styles['Heading2'], 
                textColor=colors.black,
                leftIndent=20*mm  # Décalage de 20mm vers la droite
            )
            artist_paragraph = Paragraph(artist_name, artist_style)
            elements.append(artist_paragraph)
            
            # Tableau pour chaque artiste
            for artwork in selected_artworks:
                # Ajouter le titre de l'œuvre
                elements.append(Paragraph(artwork.titre, styles['Heading3']))
                
                # Ajouter l'image si elle existe
                artwork_img = Paragraph("Aucune image", normal_style)
                if artwork.photo_path:
                    try:
                        # Chemin complet de l'image
                        image_path = os.path.join(current_app.root_path, 'app', 'static', artwork.photo_path)
                        
                        # Vérifier si l'image existe
                        if os.path.exists(image_path):
                            # Redimensionner l'image
                            img = resize_image_for_pdf(image_path)
                            
                            if img:
                                try:
                                    # Sauvegarder l'image temporairement
                                    temp_image_path = os.path.join(current_app.root_path, 'static', f'temp_artwork_{artwork.id}.png')
                                    img.save(temp_image_path)
                                    
                                    # Calculer la largeur proportionnelle
                                    img_width = img.width
                                    img_height = img.height
                                    
                                    # Créer l'image pour ReportLab
                                    artwork_img = Image(temp_image_path, width=img_width*mm/3.78, height=img_height*mm/3.78)
                                except Exception as e:
                                    current_app.logger.error(f"Erreur lors du traitement de l'image: {e}")
                                    artwork_img = Paragraph(f"Erreur de traitement: {e}", normal_style)
                            else:
                                artwork_img = Paragraph("Image non disponible", normal_style)
                    except Exception as e:
                        current_app.logger.error(f"Erreur lors du redimensionnement de l'image: {e}")
                        artwork_img = Paragraph(f"Erreur de redimensionnement: {e}", normal_style)
                
                # Créer un tableau pour chaque œuvre
                table_data = [
                    [artwork_img, Paragraph(f"""
                        <b>Titre :</b> {artwork.titre}<br/>
                        <b>Technique :</b> {artwork.technique}<br/>
                        <b>Dimensions :</b> {artwork.dimension_largeur}x{artwork.dimension_hauteur} cm<br/>
                        <b>Prix :</b> {artwork.prix} € {"" if artwork.prix else "Non défini"}
                    """, normal_style)]
                ]
                
                # Largeur totale de la page A4
                page_width = 210 * mm
                
                table = Table(table_data, colWidths=[15*mm, page_width - 15*mm], rowHeights=[70])
                table.setStyle(TableStyle([
                    ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('GRID', (0,0), (-1,-1), 1, colors.black),
                    ('BACKGROUND', (0,0), (-1,0), colors.beige)
                ]))
                
                elements.append(table)
                elements.append(Spacer(1, 12))
    
    # Construire le PDF
    doc.build(elements)
    
    # Réinitialiser le buffer
    buffer.seek(0)
    
    # Renvoyer le PDF
    return send_file(
        buffer, 
        download_name='Artworks_Selection.pdf', 
        as_attachment=True, 
        mimetype='application/pdf'
    )
