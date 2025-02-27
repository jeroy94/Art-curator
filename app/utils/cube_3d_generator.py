import os
import numpy as np
import trimesh
from PIL import Image
import logging

def create_textured_cube(image_path, depth_cm=3, output_dir=None):
    """
    Crée un cube 3D texturé à partir d'une image.
    
    Args:
        image_path (str): Chemin complet vers l'image source
        depth_cm (float, optional): Profondeur du cube en centimètres. Défaut à 3 cm.
        output_dir (str, optional): Répertoire de sortie pour le fichier OBJ. 
                                    Si None, utilise le même répertoire que l'image.
    
    Returns:
        dict: Informations sur le cube 3D créé
    """
    try:
        # Nettoyer et valider le chemin d'image
        image_path = os.path.normpath(image_path)
        if not os.path.exists(image_path):
            raise ValueError(f"Le fichier n'existe pas: {image_path}")
        
        # Charger l'image
        img = Image.open(image_path)
        width_px, height_px = img.size
        
        # Convertir les pixels en centimètres (supposons 300 DPI)
        px_to_cm = 2.54 / 300  # 1 pouce = 2.54 cm, 300 pixels par pouce
        width_cm = width_px * px_to_cm
        height_cm = height_px * px_to_cm
        
        logging.info(f"Dimensions de l'image: {width_cm:.1f}cm x {height_cm:.1f}cm")
        
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
            [0, 1, 2], [0, 2, 3],
            # Face arrière
            [5, 4, 7], [5, 7, 6],
            # Face supérieure
            [3, 2, 6], [3, 6, 7],
            # Face inférieure
            [4, 5, 1], [4, 1, 0],
            # Face gauche
            [4, 0, 3], [4, 3, 7],
            # Face droite
            [1, 5, 6], [1, 6, 2],
        ])
        
        # Créer les coordonnées de texture pour la face avant
        uv_coords = np.array([
            [0, 1],  # 0
            [1, 1],  # 1
            [1, 0],  # 2
            [0, 0],  # 3
        ])
        
        # Créer le mesh
        mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
        
        # Ajouter les informations de matériau et texture
        material = trimesh.visual.material.SimpleMaterial(image=img)
        
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
        
        # Déterminer le répertoire de sortie
        if output_dir is None:
            output_dir = os.path.dirname(image_path)
        
        # Créer le répertoire de sortie s'il n'existe pas
        os.makedirs(output_dir, exist_ok=True)
        
        # Générer le nom de fichier de sortie
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        output_obj = os.path.join(output_dir, f"{base_name}_cube.obj")
        
        # Sauvegarder le mesh
        mesh.export(output_obj)
        
        return {
            'obj_path': output_obj,
            'width_cm': width_cm,
            'height_cm': height_cm,
            'depth_cm': depth_cm
        }
    
    except Exception as e:
        logging.error(f"Erreur lors de la création du cube 3D: {e}")
        raise

def create_artwork_cube(image_path, artwork_width_cm=None, artwork_height_cm=None, depth_cm=3, output_dir=None, custom_filename=None):
    """
    Crée un cube 3D pour une œuvre avec ses dimensions réelles.
    
    Args:
        image_path (str): Chemin complet vers l'image source
        artwork_width_cm (float, optional): Largeur réelle de l'œuvre en cm
        artwork_height_cm (float, optional): Hauteur réelle de l'œuvre en cm
        depth_cm (float, optional): Profondeur du cube. Défaut à 3 cm.
        output_dir (str, optional): Répertoire de sortie. Si None, utilise le même répertoire que l'image.
        custom_filename (str, optional): Nom de fichier personnalisé pour le cube 3D
    
    Returns:
        dict: Informations sur le cube 3D créé
    """
    try:
        # Nettoyer et valider le chemin d'image
        image_path = os.path.normpath(image_path)
        if not os.path.exists(image_path):
            raise ValueError(f"Le fichier n'existe pas: {image_path}")
        
        # Charger l'image
        img = Image.open(image_path)
        width_px, height_px = img.size
        
        # Utiliser les dimensions de l'œuvre si fournies, sinon convertir à partir des pixels
        if artwork_width_cm is not None and artwork_height_cm is not None:
            width_cm = artwork_width_cm
            height_cm = artwork_height_cm
        else:
            # Convertir les pixels en centimètres (supposons 300 DPI)
            px_to_cm = 2.54 / 300  # 1 pouce = 2.54 cm, 300 pixels par pouce
            width_cm = width_px * px_to_cm
            height_cm = height_px * px_to_cm
        
        logging.info(f"Dimensions de l'œuvre: {width_cm:.1f}cm x {height_cm:.1f}cm")
        
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
            [0, 1, 2], [0, 2, 3],
            # Face arrière
            [5, 4, 7], [5, 7, 6],
            # Face supérieure
            [3, 2, 6], [3, 6, 7],
            # Face inférieure
            [4, 5, 1], [4, 1, 0],
            # Face gauche
            [4, 0, 3], [4, 3, 7],
            # Face droite
            [1, 5, 6], [1, 6, 2],
        ])
        
        # Créer les coordonnées de texture pour la face avant
        uv_coords = np.array([
            [0, 1],  # 0
            [1, 1],  # 1
            [1, 0],  # 2
            [0, 0],  # 3
        ])
        
        # Créer le mesh
        mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
        
        # Ajouter les informations de matériau et texture
        material = trimesh.visual.material.SimpleMaterial(image=img)
        
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
        
        # Déterminer le répertoire de sortie
        if output_dir is None:
            output_dir = os.path.dirname(image_path)
        
        # Créer le répertoire de sortie s'il n'existe pas
        os.makedirs(output_dir, exist_ok=True)
        
        # Générer le nom de fichier de sortie
        if custom_filename:
            output_obj = os.path.join(output_dir, f"{custom_filename}_cube.obj")
        else:
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            output_obj = os.path.join(output_dir, f"{base_name}_cube.obj")
        
        # Sauvegarder le mesh
        mesh.export(output_obj)
        
        return {
            'obj_path': output_obj,
            'width_cm': width_cm,
            'height_cm': height_cm,
            'depth_cm': depth_cm,
            'original_image_path': image_path
        }
    
    except Exception as e:
        logging.error(f"Erreur lors de la création du cube 3D: {e}")
        raise

def batch_create_3d_cubes(image_paths, depth_cm=3, output_dir=None):
    """
    Crée des cubes 3D pour un lot d'images.
    
    Args:
        image_paths (list): Liste des chemins complets vers les images
        depth_cm (float, optional): Profondeur des cubes. Défaut à 3 cm.
        output_dir (str, optional): Répertoire de sortie. Si None, utilise le même répertoire que les images.
    
    Returns:
        list: Liste des informations sur les cubes 3D créés
    """
    results = []
    for image_path in image_paths:
        try:
            cube_info = create_textured_cube(image_path, depth_cm, output_dir)
            results.append(cube_info)
        except Exception as e:
            logging.warning(f"Impossible de créer un cube 3D pour {image_path}: {e}")
    
    return results
