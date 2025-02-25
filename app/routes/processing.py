"""
Routes pour le traitement des images et la génération de modèles 3D.
"""
from flask import Blueprint, request, jsonify, current_app
import os
from werkzeug.utils import secure_filename
from ..image_processing.processor import ImageProcessor
from ..image_processing.validator import ImageValidator, MeshValidator

bp = Blueprint('processing', __name__)

def allowed_file(filename):
    """Vérifie si l'extension du fichier est autorisée."""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/process', methods=['POST'])
def process_image():
    """
    Traite une image pour créer un modèle 3D.
    
    L'image doit être envoyée dans un formulaire multipart avec le champ 'image'.
    """
    # Vérifier si un fichier a été envoyé
    if 'image' not in request.files:
        return jsonify({'error': 'Aucun fichier envoyé'}), 400
        
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400
        
    if file and allowed_file(file.filename):
        # Sécuriser le nom du fichier
        filename = secure_filename(file.filename)
        
        # Créer les chemins pour les fichiers
        input_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'input', filename)
        output_filename = os.path.splitext(filename)[0] + '.obj'
        output_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'output', output_filename)
        
        # Créer les dossiers si nécessaire
        os.makedirs(os.path.dirname(input_path), exist_ok=True)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Sauvegarder l'image
        file.save(input_path)
        
        # Valider l'image
        is_valid, message = ImageValidator.validate_image(input_path)
        if not is_valid:
            os.remove(input_path)
            return jsonify({'error': message}), 400
            
        try:
            # Traiter l'image
            processor = ImageProcessor(input_path)
            processor.process_image_to_3d(output_path)
            
            # Valider le maillage généré
            is_valid, message = MeshValidator.validate_mesh(output_path)
            if not is_valid:
                os.remove(output_path)
                return jsonify({'error': message}), 400
                
            return jsonify({
                'message': 'Traitement réussi',
                'output_file': output_filename
            }), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    return jsonify({'error': 'Type de fichier non autorisé'}), 400
