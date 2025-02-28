from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models.models import db, User
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
            return redirect(next_page or url_for('main.index'))
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
    
    db.session.commit()
    flash('Profil mis à jour avec succès', 'success')
    return redirect(url_for('auth.profile'))
