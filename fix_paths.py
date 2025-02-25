import sqlite3
import os

def fix_photo_paths():
    # Connexion à la base de données
    conn = sqlite3.connect('instance/art_database.db')
    cursor = conn.cursor()

    print("=== Correction des chemins d'images ===")
    
    # Récupérer tous les chemins d'images
    cursor.execute("SELECT id, photo_path FROM artworks WHERE photo_path IS NOT NULL")
    artworks = cursor.fetchall()
    
    for artwork_id, photo_path in artworks:
        if photo_path:
            # Obtenir juste le nom du fichier
            filename = os.path.basename(photo_path)
            # Construire le nouveau chemin
            new_path = os.path.join('uploads', 'artworks', filename)
            
            print(f"ID {artwork_id}:")
            print(f"  Ancien chemin: {photo_path}")
            print(f"  Nouveau chemin: {new_path}")
            
            # Mettre à jour le chemin dans la base de données
            cursor.execute(
                "UPDATE artworks SET photo_path = ? WHERE id = ?",
                (new_path.replace('\\', '/'), artwork_id)
            )
    
    # Sauvegarder les changements
    conn.commit()
    print("\nMise à jour terminée!")
    
    # Vérifier les nouveaux chemins
    print("\n=== Nouveaux chemins dans la base de données ===")
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

if __name__ == '__main__':
    fix_photo_paths()
