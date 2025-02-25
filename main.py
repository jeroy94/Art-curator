import numpy as np
import cv2
import trimesh
from PIL import Image
import os

def create_textured_cube(image_path, depth_cm=3):
    # Nettoyer le chemin d'accès des guillemets
    image_path = image_path.strip('"').strip("'").strip()
    
    # Vérifier si le fichier existe
    if not os.path.exists(image_path):
        raise ValueError(f"Le fichier n'existe pas: {image_path}")
    
    # Charger l'image avec PIL pour obtenir ses dimensions en pixels
    img = Image.open(image_path)
    width_px, height_px = img.size
    
    # Convertir les pixels en centimètres (supposons 300 DPI)
    px_to_cm = 2.54 / 300  # 1 pouce = 2.54 cm, 300 pixels par pouce
    width_cm = width_px * px_to_cm
    height_cm = height_px * px_to_cm
    
    print(f"Dimensions de l'image: {width_cm:.1f}cm x {height_cm:.1f}cm")
    
    # Créer les vertices du cube (en cm)
    vertices = np.array([
        # Face avant (avec l'image)
        [0, 0, 0],          # 0
        [width_cm, 0, 0],   # 1
        [width_cm, height_cm, 0], # 2
        [0, height_cm, 0],  # 3
        # Face arrière
        [0, 0, -depth_cm],         # 4
        [width_cm, 0, -depth_cm],  # 5
        [width_cm, height_cm, -depth_cm], # 6
        [0, height_cm, -depth_cm], # 7
    ])
    
    # Définir les faces (triangles)
    faces = np.array([
        # Face avant (avec l'image)
        [0, 1, 2],
        [0, 2, 3],
        # Face arrière
        [5, 4, 7],
        [5, 7, 6],
        # Face supérieure
        [3, 2, 6],
        [3, 6, 7],
        # Face inférieure
        [4, 5, 1],
        [4, 1, 0],
        # Face gauche
        [4, 0, 3],
        [4, 3, 7],
        # Face droite
        [1, 5, 6],
        [1, 6, 2],
    ])
    
    # Créer les coordonnées de texture pour la face avant
    uv_coords = np.array([
        [0, 1],  # 0
        [1, 1],  # 1
        [1, 0],  # 2
        [0, 0],  # 3
    ])
    
    # Créer le mesh
    mesh = trimesh.Trimesh(
        vertices=vertices,
        faces=faces,
    )
    
    # Ajouter les informations de matériau et texture
    material = trimesh.visual.material.SimpleMaterial(
        image=img
    )
    
    # Assigner la texture à la face avant seulement
    face_materials = np.zeros(len(faces), dtype=np.int32)
    face_materials[0:2] = 0  # Les deux premiers triangles (face avant) utilisent le matériau
    
    # Créer les coordonnées UV pour toutes les faces
    face_uvs = np.zeros((len(faces), 3, 2))
    # Assigner les coordonnées UV à la face avant
    face_uvs[0] = uv_coords[[0, 1, 2]]  # Premier triangle
    face_uvs[1] = uv_coords[[0, 2, 3]]  # Deuxième triangle
    
    # Appliquer la texture
    mesh.visual = trimesh.visual.TextureVisuals(
        uv=face_uvs,
        material=material,
        face_materials=face_materials
    )
    
    return mesh

def main():
    try:
        # Demander le chemin de l'image et le nettoyer
        image_path = input("Entrez le chemin de votre image: ").strip('"').strip("'").strip()
        print(f"Tentative de chargement de l'image: {image_path}")
        
        # Créer le cube texturé
        mesh = create_textured_cube(image_path)
        
        # Créer le chemin de sortie
        output_dir = os.path.dirname(image_path)
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        output_obj = os.path.join(output_dir, f"{base_name}_cube.obj")
        
        # Sauvegarder en format OBJ et MTL
        mesh.export(output_obj)
        print(f"Cube 3D créé avec succès! Sauvegardé sous: {output_obj}")
        
        # Afficher une prévisualisation
        mesh.show()
        
    except Exception as e:
        print(f"Erreur: {str(e)}")
        print("Assurez-vous que:")
        print("1. Le chemin de l'image est correct")
        print("2. Vous avez les permissions pour accéder au fichier")
        print("3. L'image est dans un format supporté (PNG, JPG, etc.)")

if __name__ == "__main__":
    main()
