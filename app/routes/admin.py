from flask import Blueprint, jsonify, request, current_app, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.models import Artist, Artwork, db, Vote, User, Invitation
from functools import wraps
import secrets
from datetime import datetime, timedelta
from app.utils.email_sender import send_invitation_email
from flask_mail import Mail
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Accès administrateur requis', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    artworks = Artwork.query.all()
    users = User.query.all()
    return render_template('admin/dashboard.html', 
                         artworks=artworks, 
                         users=users)

@admin_bp.route('/artists')
@login_required
@admin_required
def list_artists():
    artists = Artist.query.all()
    return render_template('admin/artists.html', artists=artists)

@admin_bp.route('/artworks')
@login_required
@admin_required
def list_artworks():
    artworks = Artwork.query.all()
    return render_template('admin/artworks.html', artworks=artworks)

@admin_bp.route('/artwork/<int:artwork_id>/selection', methods=['POST'])
@login_required
@admin_required
def update_artwork_selection(artwork_id):
    artwork = Artwork.query.get_or_404(artwork_id)
    artwork.statut = 'selectionne'
    db.session.commit()
    flash('Statut de l\'œuvre mis à jour', 'success')
    return redirect(url_for('admin.list_artworks'))

@admin_bp.route('/statistics')
@login_required
@admin_required
def get_statistics():
    stats = {
        'total_artworks': Artwork.query.count(),
        'total_artists': Artist.query.count(),
        'total_votes': Vote.query.count()
    }
    return render_template('admin/statistics.html', stats=stats)

@admin_bp.route('/generate-pdfs')
@login_required
@admin_required
def generate_pdfs():
    # Logique de génération des PDF
    flash('Génération des PDF en cours...', 'info')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/invite_member', methods=['GET', 'POST'])
@login_required
@admin_required
def invite_member():
    """Inviter un nouveau membre ou artiste."""
    if request.method == 'POST':
        email = request.form.get('email')
        role = request.form.get('role', 'membre')
        
        # Vérifier que le rôle est valide
        if role not in ['membre', 'artiste']:
            flash('Rôle invalide.', 'danger')
            return render_template('admin/invite_member.html')
        
        # Vérifier si l'email existe déjà
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Un utilisateur avec cet email existe déjà.', 'danger')
            return render_template('admin/invite_member.html')
        
        # Générer un token unique
        token = secrets.token_urlsafe(32)
        
        # Définir la date d'expiration (7 jours)
        current_time = datetime.utcnow()
        expires_at = current_time + timedelta(days=7)
        
        try:
            # Créer l'invitation
            invitation = Invitation(
                email=email,
                role=role,
                token=token,
                created_at=current_time,
                expires_at=expires_at
            )
            
            # Ajouter et committer l'invitation
            db.session.add(invitation)
            db.session.commit()
            
            # Envoyer l'email d'invitation
            send_invitation_email(email, token, role)
            
            flash('Invitation envoyée avec succès.', 'success')
            return redirect(url_for('admin.invite_member'))
        
        except IntegrityError:
            db.session.rollback()
            flash('Une invitation pour cet email existe déjà.', 'warning')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erreur lors de l'invitation : {e}")
            flash('Une erreur est survenue lors de l\'envoi de l\'invitation.', 'danger')
    
    return render_template('admin/invite_member.html')

@admin_bp.route('/accept_invitation/<string:token>', methods=['GET', 'POST'])
def accept_invitation(token):
    """Page d'acceptation de l'invitation."""
    current_app.logger.info(f"Tentative d'acceptation d'invitation avec le token : {token}")
    current_app.logger.info(f"URL complète de la requête : {request.url}")
    current_app.logger.info(f"Méthode de la requête : {request.method}")
    
    # Vérifier le token d'invitation
    try:
        # Rechercher l'invitation par token
        invitation = Invitation.query.filter_by(token=token).first()
        
        if not invitation:
            current_app.logger.warning(f"Aucune invitation trouvée pour le token : {token}")
            flash('Le lien d\'invitation est invalide.', 'danger')
            return redirect(url_for('main.index'))
        
        # Vérifier l'expiration
        current_time = datetime.utcnow()
        if invitation.expires_at <= current_time:
            current_app.logger.warning(f"Invitation expirée pour le token : {token}")
            flash('Le lien d\'invitation a expiré.', 'danger')
            return redirect(url_for('main.index'))
        
        # Logs détaillés sur l'invitation
        current_app.logger.info(f"Détails de l'invitation : email={invitation.email}, role={invitation.role}")
        current_app.logger.info(f"Date de création : {invitation.created_at}")
        current_app.logger.info(f"Date d'expiration : {invitation.expires_at}")
    
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la vérification de l'invitation : {e}")
        flash('Une erreur est survenue lors du traitement de votre invitation.', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Vérifier si le nom d'utilisateur existe déjà
        existing_user = User.query.filter_by(username=username).first()
        
        if existing_user:
            current_app.logger.warning(f"Nom d'utilisateur déjà existant : {username}")
            flash('Ce nom d\'utilisateur est déjà utilisé.', 'danger')
        else:
            # Créer le nouvel utilisateur
            new_user = User(
                email=invitation.email,
                username=username,
                is_membre=invitation.role == 'membre',
                is_artiste=invitation.role == 'artiste'
            )
            new_user.set_password(password)
            
            try:
                db.session.add(new_user)
                
                # Supprimer l'invitation
                db.session.delete(invitation)
                db.session.commit()
                
                current_app.logger.info(f"Compte créé avec succès pour {username}")
                flash('Compte créé avec succès. Vous pouvez maintenant vous connecter.', 'success')
                return redirect(url_for('auth.login'))
            
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Erreur lors de la création du compte : {e}")
                flash('Une erreur est survenue lors de la création de votre compte.', 'danger')
    
    return render_template('auth/accept_invitation.html', email=invitation.email, token=token)

@admin_bp.route('/debug_routes')
def debug_routes():
    """Route de débogage pour lister toutes les routes du blueprint admin."""
    routes = []
    for rule in current_app.url_map.iter_rules():
        if rule.endpoint.startswith('admin.'):
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'route': str(rule)
            })
    
    # Log des routes
    current_app.logger.info("Routes du blueprint admin :")
    for route in routes:
        current_app.logger.info(f"Endpoint: {route['endpoint']}")
        current_app.logger.info(f"  Méthodes : {route['methods']}")
        current_app.logger.info(f"  Chemin : {route['route']}")
    
    return render_template('admin/debug_routes.html', routes=routes)
