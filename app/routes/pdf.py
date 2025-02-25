from flask import Blueprint, send_file, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.models import Artwork, Artist, db
from ..services.pdf_generator import PDFGenerator
from io import BytesIO

pdf_bp = Blueprint('pdf', __name__)
pdf_generator = PDFGenerator()

@pdf_bp.route('/generate/catalog', methods=['GET'])
@jwt_required()
def generate_catalog():
    try:
        # Récupérer toutes les œuvres sélectionnées
        selected_artworks = Artwork.query.filter_by(selectionne=True).all()
        
        if not selected_artworks:
            return jsonify({
                'error': 'Aucune œuvre sélectionnée trouvée'
            }), 404

        # Créer un buffer pour le PDF
        buffer = BytesIO()
        
        # Générer le PDF
        pdf_generator.generate_catalog(selected_artworks, buffer)
        
        # Rembobiner le buffer et l'envoyer
        buffer.seek(0)
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='catalogue_oeuvres.pdf'
        )

    except Exception as e:
        return jsonify({
            'error': f'Erreur lors de la génération du PDF: {str(e)}'
        }), 500

@pdf_bp.route('/generate/artist-summary/<int:artist_id>', methods=['GET'])
@jwt_required()
def generate_artist_summary(artist_id):
    try:
        # Récupérer l'artiste et ses œuvres
        artist = Artist.query.get(artist_id)
        if not artist:
            return jsonify({
                'error': 'Artiste non trouvé'
            }), 404

        artworks = Artwork.query.filter_by(artist_id=artist_id).all()
        
        # Créer un buffer pour le PDF
        buffer = BytesIO()
        
        # Générer le PDF
        pdf_generator.generate_artist_summary(artist, artworks, buffer)
        
        # Rembobiner le buffer et l'envoyer
        buffer.seek(0)
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'resume_artiste_{artist.nom}_{artist.prenom}.pdf'
        )

    except Exception as e:
        return jsonify({
            'error': f'Erreur lors de la génération du PDF: {str(e)}'
        }), 500
