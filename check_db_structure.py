from app import create_app
from app.models.models import db, Artwork
import sqlite3

app = create_app()

with app.app_context():
    # Vérifier la structure via SQLAlchemy
    print("Structure de la table via SQLAlchemy:")
    for column in Artwork.__table__.columns:
        print(f"- {column.name}: {column.type}")

    # Vérifier directement avec SQLite
    print("\nStructure de la table via SQLite:")
    conn = sqlite3.connect('instance/art_database.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(artworks)")
    columns = cursor.fetchall()
    for column in columns:
        print(f"- {column[1]}: {column[2]}")
    conn.close()
