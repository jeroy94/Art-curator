"""
Processeur principal pour la conversion d'images en modèles 3D.
"""
import os
import cv2
import numpy as np
import trimesh
from PIL import Image
from scipy.ndimage import gaussian_filter

class ImageProcessor:
    def __init__(self, image_path):
        """
        Initialise le processeur d'image.
        
        Args:
            image_path (str): Chemin vers l'image à traiter
        """
        self.image_path = image_path
        self.image = None
        self.depth_map = None
        self.mesh = None
        
    def load_image(self):
        """Charge l'image et la convertit en niveaux de gris."""
        self.image = cv2.imread(self.image_path, cv2.IMREAD_GRAYSCALE)
        if self.image is None:
            raise ValueError(f"Impossible de charger l'image: {self.image_path}")
        return self.image
        
    def create_depth_map(self, blur_sigma=2.0):
        """
        Crée une carte de profondeur à partir de l'image en niveaux de gris.
        
        Args:
            blur_sigma (float): Force du flou gaussien
        """
        if self.image is None:
            self.load_image()
            
        # Appliquer un flou gaussien pour réduire le bruit
        self.depth_map = gaussian_filter(self.image.astype(float), sigma=blur_sigma)
        
        # Normaliser les valeurs entre 0 et 1
        self.depth_map = (self.depth_map - self.depth_map.min()) / (self.depth_map.max() - self.depth_map.min())
        return self.depth_map
        
    def generate_mesh(self, scale_factor=1.0):
        """
        Génère un maillage 3D à partir de la carte de profondeur.
        
        Args:
            scale_factor (float): Facteur d'échelle pour la hauteur du maillage
        """
        if self.depth_map is None:
            self.create_depth_map()
            
        height, width = self.depth_map.shape
        
        # Créer les coordonnées x, y
        x, y = np.meshgrid(np.arange(width), np.arange(height))
        
        # Créer les vertices
        vertices = np.stack([x.flatten(), y.flatten(), self.depth_map.flatten() * scale_factor], axis=1)
        
        # Créer les faces
        faces = []
        for i in range(height - 1):
            for j in range(width - 1):
                v0 = i * width + j
                v1 = v0 + 1
                v2 = (i + 1) * width + j
                v3 = v2 + 1
                faces.extend([[v0, v1, v2], [v1, v3, v2]])
                
        faces = np.array(faces)
        
        # Créer le maillage
        self.mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
        return self.mesh
        
    def save_mesh(self, output_path):
        """
        Sauvegarde le maillage au format OBJ.
        
        Args:
            output_path (str): Chemin de sortie pour le fichier OBJ
        """
        if self.mesh is None:
            raise ValueError("Aucun maillage n'a été généré")
            
        self.mesh.export(output_path)
        return output_path
        
    def process_image_to_3d(self, output_path, scale_factor=1.0, blur_sigma=2.0):
        """
        Traite une image en un modèle 3D en une seule étape.
        
        Args:
            output_path (str): Chemin de sortie pour le fichier OBJ
            scale_factor (float): Facteur d'échelle pour la hauteur du maillage
            blur_sigma (float): Force du flou gaussien
        """
        self.load_image()
        self.create_depth_map(blur_sigma=blur_sigma)
        self.generate_mesh(scale_factor=scale_factor)
        return self.save_mesh(output_path)
