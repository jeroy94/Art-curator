import os
import sys
import click
from flask import Flask
from flask.cli import with_appcontext

# Ajouter le chemin du projet au PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.models import db, User

@click.command('reset-db')
@with_appcontext
def reset_database_command():
    """Réinitialise la base de données et crée des utilisateurs par défaut."""
    # Supprimer toutes les tables existantes
    db.drop_all()
    
    # Recréer les tables
    db.create_all()
    click.echo("Base de données réinitialisée")

    # Créer l'utilisateur admin
    admin = User(
        username='admin_cartel',
        email='admin@artcartel.com', 
        is_admin=True
    )
    admin.set_password('AdminCartel2025!')
    db.session.add(admin)

    # Créer des membres
    membres = [
        User(username='membre1', email='membre1@artcartel.com', is_membre=True),
        User(username='membre2', email='membre2@artcartel.com', is_membre=True),
        User(username='membre3', email='membre3@artcartel.com', is_membre=True)
    ]
    for membre in membres:
        membre.set_password(f'{membre.username}Cartel2025!')
        db.session.add(membre)

    # Créer des artistes
    artistes = [
        User(username='artiste1', email='artiste1@artcartel.com', is_artiste=True),
        User(username='artiste2', email='artiste2@artcartel.com', is_artiste=True)
    ]
    for artiste in artistes:
        artiste.set_password(f'{artiste.username}Cartel2025!')
        db.session.add(artiste)

    # Commit des utilisateurs
    db.session.commit()
    click.echo("Utilisateurs créés avec succès")

def init_app(app):
    """Initialises la commande de réinitialisation de base de données."""
    app.cli.add_command(reset_database_command)

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        reset_database_command()
