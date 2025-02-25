from flask import Blueprint, jsonify
from app.models.models import db, Artwork, Artist, User

bp = Blueprint('test', __name__, url_prefix='/api/test')

@bp.route('/db-status', methods=['GET'])
def db_status():
    try:
        artworks_count = Artwork.query.count()
        artists_count = Artist.query.count()
        users_count = User.query.count()
        
        return jsonify({
            'status': 'ok',
            'counts': {
                'artworks': artworks_count,
                'artists': artists_count,
                'users': users_count
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@bp.route('/test', methods=['GET'])
def test():
    return jsonify({
        'message': 'API fonctionne correctement',
        'status': 'success'
    })

@bp.route('/create-admin', methods=['GET'])
def create_admin():
    # Créer un utilisateur admin pour les tests
    if not User.query.filter_by(email='admin@test.com').first():
        admin = User(
            username='admin',
            email='admin@test.com',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        return jsonify({
            'message': 'Administrateur créé avec succès',
            'credentials': {
                'email': 'admin@test.com',
                'password': 'admin123'
            }
        })
    return jsonify({
        'message': 'Un administrateur existe déjà',
        'credentials': {
            'email': 'admin@test.com',
            'password': 'admin123'
        }
    })

@bp.route('/reset-db', methods=['POST'])
def reset_db():
    try:
        # Supprimer toutes les œuvres
        Artwork.query.delete()
        # Supprimer tous les artistes
        Artist.query.delete()
        # Garder l'utilisateur admin
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Base de données réinitialisée avec succès'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@bp.route('/reset', methods=['POST'])
def reset_database():
    try:
        # Supprimer toutes les données
        Artwork.query.delete()
        Artist.query.delete()
        User.query.filter(User.is_admin == False).delete()
        db.session.commit()
        
        return jsonify({'message': 'Base de données réinitialisée avec succès'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/seed', methods=['POST'])
def seed_database():
    try:
        # Créer des artistes de test
        artist1 = Artist(
            nom='Dupont',
            prenom='Jean',
            email='jean.dupont@test.com',
            categorie='peinture'
        )
        
        artist2 = Artist(
            nom='Martin',
            prenom='Marie',
            email='marie.martin@test.com',
            categorie='sculpture'
        )
        
        db.session.add(artist1)
        db.session.add(artist2)
        db.session.flush()  # Pour obtenir les IDs
        
        # Créer des œuvres de test
        artwork1 = Artwork(
            title='Nature morte',
            description='Une belle nature morte',
            technique='Huile sur toile',
            dimensions='50x70',
            year=2023,
            price=1000,
            artist_id=artist1.id
        )
        
        artwork2 = Artwork(
            title='Le penseur moderne',
            description='Sculpture contemporaine',
            technique='Bronze',
            dimensions='30x40x50',
            year=2023,
            price=2000,
            artist_id=artist2.id
        )
        
        db.session.add(artwork1)
        db.session.add(artwork2)
        db.session.commit()
        
        return jsonify({'message': 'Données de test ajoutées avec succès'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
