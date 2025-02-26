from flask import Blueprint, render_template, send_from_directory, current_app, request, jsonify, redirect, url_for, flash, session
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
                        artwork_id = int(key.split('_')[1])
                        votes[artwork_id] = value
                
                current_app.logger.info(f"Votes reçus : {votes}")
                
                for artwork_id, vote_value in votes.items():
                    current_app.logger.info(f"Mise à jour du vote pour l'œuvre {artwork_id} ")
                    update_artwork_vote(artwork_id, vote_value, current_user)

            elif action == 'selection' and current_user.is_admin:
                selections = {}
                for key, value in request.form.items():
                    if key.startswith('selection_'):
                        artwork_id = int(key.split('_')[1])
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
