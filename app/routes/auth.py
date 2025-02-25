from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models.models import db, User, Artist
from datetime import timedelta, datetime
from werkzeug.security import generate_password_hash

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            flash('Email déjà utilisé', 'danger')
            return redirect(url_for('auth.register'))
            
        if User.query.filter_by(username=username).first():
            flash('Nom d\'utilisateur déjà utilisé', 'danger')
            return redirect(url_for('auth.register'))
            
        user = User(
            username=username,
            email=email
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Inscription réussie ! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False) == 'on'
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash('Connexion réussie !', 'success')
            next_page = request.args.get('next')
            if user.is_admin:
                return redirect(next_page or url_for('admin.dashboard'))
            else:
                return redirect(next_page or url_for('artworks.list'))
        else:
            flash('Email ou mot de passe incorrect', 'danger')
            
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté', 'info')
    return redirect(url_for('main.index'))

@bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html')

@bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    username = request.form.get('username')
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    is_artist = request.form.get('is_artist') == 'on'
    
    if username != current_user.username:
        if User.query.filter_by(username=username).first():
            flash('Ce nom d\'utilisateur est déjà utilisé', 'danger')
            return redirect(url_for('auth.profile'))
        current_user.username = username
    
    if current_password and new_password:
        if not current_user.check_password(current_password):
            flash('Mot de passe actuel incorrect', 'danger')
            return redirect(url_for('auth.profile'))
            
        if new_password != confirm_password:
            flash('Les nouveaux mots de passe ne correspondent pas', 'danger')
            return redirect(url_for('auth.profile'))
            
        current_user.set_password(new_password)
    
    if is_artist != current_user.is_artist:
        current_user.is_artist = is_artist
        if is_artist and not current_user.artist:
            artist = Artist(user_id=current_user.id)
            db.session.add(artist)
    
    db.session.commit()
    flash('Profil mis à jour avec succès', 'success')
    return redirect(url_for('auth.profile'))

@bp.route('/register/artist', methods=['POST'])
def register_artist():
    try:
        data = request.get_json()
        
        # Vérifier les champs obligatoires
        required_fields = ['nom', 'prenom', 'email', 'password', 'type_artiste']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Le champ {field} est obligatoire'}), 400
        
        # Vérifier si l'email existe déjà
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Cet email est déjà utilisé'}), 400
        
        # Générer le numéro de dossier
        current_year = datetime.now().year
        count = Artist.query.filter(Artist.created_at >= datetime(current_year, 1, 1)).count()
        numero_dossier = f"{current_year}-{count + 1:03d}"
        
        # Créer l'utilisateur
        user = User(
            username=data['email'],
            email=data['email']
        )
        user.set_password(data['password'])
        db.session.add(user)
        
        # Créer l'artiste
        artist = Artist(
            numero_dossier=numero_dossier,
            nom=data['nom'],
            prenom=data['prenom'],
            nom_artiste=data.get('nom_artiste', ''),
            email=data['email'],
            telephone=data.get('telephone', ''),
            adresse=data.get('adresse', ''),
            categorie=data['type_artiste']
        )
        
        db.session.add(artist)
        db.session.commit()
        
        # Créer le token JWT
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'Inscription réussie',
            'artist_id': artist.id,
            'numero_dossier': artist.numero_dossier,
            'token': access_token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Erreur lors de l'inscription de l'artiste: {str(e)}")
        return jsonify({'error': "Une erreur est survenue lors de l'inscription"}), 500

@bp.route('/login/artist', methods=['POST'])
def login_artist():
    data = request.get_json()
    artist = Artist.query.filter_by(email=data['email']).first()
    
    if artist and artist.check_password(data['password']):
        access_token = create_access_token(identity=f"artist_{artist.id}")
        return jsonify({
            'access_token': access_token,
            'type_artiste': artist.type_artiste
        })
    
    return jsonify({'error': 'Email ou mot de passe incorrect'}), 401
