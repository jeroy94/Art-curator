from flask import current_app
from app.models.models import db
from sqlalchemy import Column, String

def upgrade():
    """Ajoute la colonne status à la table invitations."""
    with current_app.app_context():
        # Vérifier si la colonne existe déjà
        inspector = db.inspect(db.engine)
        columns = inspector.get_columns('invitations')
        column_names = [column['name'] for column in columns]
        
        if 'status' not in column_names:
            # Ajouter la colonne status avec une valeur par défaut
            with db.engine.begin() as connection:
                connection.execute('''
                    ALTER TABLE invitations 
                    ADD COLUMN status VARCHAR(20) DEFAULT 'pending' NOT NULL
                ''')
            print("Colonne 'status' ajoutée à la table 'invitations'")
        else:
            print("La colonne 'status' existe déjà")

def downgrade():
    """Supprime la colonne status de la table invitations."""
    with current_app.app_context():
        # Vérifier si la colonne existe
        inspector = db.inspect(db.engine)
        columns = inspector.get_columns('invitations')
        column_names = [column['name'] for column in columns]
        
        if 'status' in column_names:
            with db.engine.begin() as connection:
                connection.execute('''
                    ALTER TABLE invitations 
                    DROP COLUMN status
                ''')
            print("Colonne 'status' supprimée de la table 'invitations'")
        else:
            print("La colonne 'status' n'existe pas")
