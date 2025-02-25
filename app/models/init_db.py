from flask import current_app
from app.models.models import db, User, Artist, Artwork

def init_database(app):
    """Initialize the database with tables and default admin user"""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create admin user if it doesn't exist
        if not User.query.filter_by(email='admin@example.com').first():
            admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()

def reset_database(app):
    """Reset the database by dropping all tables and recreating them"""
    with app.app_context():
        db.drop_all()
        db.create_all()
        init_database(app)