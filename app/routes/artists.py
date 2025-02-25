from flask import Blueprint, render_template, flash, redirect, url_for, request, current_app
from app.models.models import db, Artist, Artwork
from werkzeug.utils import secure_filename
import os
from datetime import datetime

bp = Blueprint('artists', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/submit', methods=['GET', 'POST'])
def submit_artwork():
    if request.method == 'GET':
        return render_template('artists/submit_artwork.html')

    if request.method == 'POST':
        # Créer ou récupérer l'artiste
        artist = Artist.query.filter_by(email=request.form['email']).first()
        
        if not artist:
            artist = Artist(
                civilite=request.form.get('civilite'),
                nom=request.form['nom'],
                prenom=request.form['prenom'],
                nom_artiste=request.form.get('nom_artiste', ''),
                prenom_artiste=request.form.get('prenom_artiste', ''),
                adresse=request.form['adresse'],
                code_postal=request.form['code_postal'],
                ville=request.form['ville'],
                pays=request.form.get('pays', 'France'),
                telephone=request.form['telephone'],
                email=request.form['email'],
                site_internet=request.form.get('site_internet', ''),
                facebook=request.form.get('facebook', ''),
                numero_mda=request.form.get('numero_mda', ''),
                numero_siret=request.form.get('numero_siret', ''),
                categorie=request.form['categorie'],
                nom_catalogue=request.form['nom_catalogue'],
                edition_adresse=bool(request.form.get('edition_adresse')),
                edition_telephone=bool(request.form.get('edition_telephone')),
                edition_email=bool(request.form.get('edition_email')),
                edition_site=bool(request.form.get('edition_site')),
                edition_facebook=bool(request.form.get('edition_facebook'))
            )
            db.session.add(artist)
            db.session.commit()

        # Traiter chaque œuvre
        for i in range(1, 11):
            titre = request.form.get(f'titre_{i}')
            if titre:  # Si un titre est fourni, on traite cette œuvre
                photo = request.files.get(f'photo_{i}')
                
                if not photo or photo.filename == '':
                    flash(f'Photo manquante pour l\'œuvre {i}', 'danger')
                    continue
                    
                # Traiter la photo si elle existe
                photo_path = None
                if photo and photo.filename:
                    if allowed_file(photo.filename):
                        # Générer un nom de fichier unique
                        filename = f"{artist.id}_{secure_filename(photo.filename)}"
                        
                        # S'assurer que le dossier uploads/artworks existe
                        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'artworks')
                        os.makedirs(upload_folder, exist_ok=True)
                        
                        # Sauvegarder la photo
                        photo_path = os.path.join('uploads', 'artworks', filename)
                        full_path = os.path.join(current_app.root_path, 'static', 'uploads', 'artworks', filename)
                        photo.save(full_path)
                    else:
                        flash(f'Format de fichier non autorisé pour l\'œuvre {i}. Utilisez JPG, PNG ou GIF.', 'danger')
                        continue

                # Créer l'œuvre
                artwork = Artwork(
                    numero=f"{artist.id}-{i}",
                    titre=request.form.get(f'titre_{i}'),
                    technique=request.form.get(f'technique_{i}', ''),
                    dimension_largeur=float(request.form.get(f'largeur_{i}', 0)),
                    dimension_hauteur=float(request.form.get(f'hauteur_{i}', 0)),
                    dimension_profondeur=float(request.form.get(f'profondeur_{i}', 0)),
                    prix=float(request.form.get(f'prix_{i}', 0)),
                    photo_path=photo_path,
                    artist_id=artist.id,
                    statut='en_attente'
                )
                db.session.add(artwork)

        db.session.commit()
        flash('Vos œuvres ont été soumises avec succès !', 'success')
        return redirect(url_for('main.index'))

    return render_template('artists/submit_artwork.html')
