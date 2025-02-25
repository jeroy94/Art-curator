import sqlite3

# Connexion à la base de données
conn = sqlite3.connect('instance/art_database.db')
cursor = conn.cursor()

# Afficher les chemins des images
print("=== Chemins des images dans la base de données ===")
cursor.execute("""
    SELECT a.id, a.titre, a.photo_path, ar.nom, ar.prenom 
    FROM artworks a 
    JOIN artists ar ON a.artist_id = ar.id 
    WHERE a.photo_path IS NOT NULL
""")
for row in cursor.fetchall():
    print(f"ID: {row[0]}, Titre: {row[1]}")
    print(f"Artiste: {row[3]} {row[4]}")
    print(f"Chemin: {row[2]}")
    print()

conn.close()
