"""
Validateur pour les images et les modèles 3D générés.
"""
import os
import cv2
import numpy as np
from PIL import Image
import trimesh

class ImageValidator:
    """Classe pour valider les images avant traitement."""
    
    @staticmethod
    def validate_image(image_path):
        """
        Valide une image avant le traitement.
        
        Args:
            image_path (str): Chemin vers l'image à valider
            
        Returns:
            tuple: (bool, str) - (est_valide, message)
        """
        if not os.path.exists(image_path):
            return False, "Le fichier n'existe pas"
            
        try:
            img = Image.open(image_path)
            
            # Vérifier le format
            if img.format not in ['JPEG', 'PNG', 'BMP']:
                return False, f"Format non supporté: {img.format}"
                
            # Vérifier les dimensions
            width, height = img.size
            if width < 100 or height < 100:
                return False, f"Image trop petite: {width}x{height}"
            if width > 4096 or height > 4096:
                return False, f"Image trop grande: {width}x{height}"
                
            # Vérifier le mode de couleur
            if img.mode not in ['RGB', 'L']:
                return False, f"Mode couleur non supporté: {img.mode}"
                
            return True, "Image valide"
            
        except Exception as e:
            return False, f"Erreur lors de la validation: {str(e)}"
            
class MeshValidator:
    """Classe pour valider les modèles 3D générés."""
    
    @staticmethod
    def validate_mesh(mesh_path):
        """
        Valide un maillage 3D.
        
        Args:
            mesh_path (str): Chemin vers le fichier de maillage
            
        Returns:
            tuple: (bool, str) - (est_valide, message)
        """
        if not os.path.exists(mesh_path):
            return False, "Le fichier n'existe pas"
            
        try:
            mesh = trimesh.load(mesh_path)
            
            # Vérifier si le maillage est vide
            if mesh.is_empty:
                return False, "Le maillage est vide"
                
            # Vérifier la topologie
            if not mesh.is_watertight:
                return False, "Le maillage n'est pas étanche"
                
            # Vérifier les normales
            if not mesh.is_winding_consistent:
                return False, "Les normales ne sont pas cohérentes"
                
            return True, "Maillage valide"
            
        except Exception as e:
            return False, f"Erreur lors de la validation: {str(e)}"
