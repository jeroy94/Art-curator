export interface Artist {
  id: number;
  nom: string;
  prenom: string;
  nom_artiste: string;
  email: string;
  telephone?: string;
  adresse?: string;
  type_artiste: 'Peintre' | 'Photographe' | 'Numérique' | 'Sculpteur';
}

export interface Artwork {
  id: number;
  nom: string;
  prix: number;
  technique: string;
  photo_path: string;
  date_soumission: string;
  selectionne: boolean;
  votes: number;
  artist: Artist;
  type_oeuvre: 'Peinture' | 'Photo' | 'Numérique' | 'Sculpture';
  
  // Champs spécifiques pour peintures, photos, art numérique
  dimension_hors_cadre_hauteur?: number;
  dimension_hors_cadre_largeur?: number;
  dimension_avec_cadre_hauteur?: number;
  dimension_avec_cadre_largeur?: number;
  
  // Champs spécifiques pour sculptures
  dimension_hauteur?: number;
  dimension_largeur?: number;
  dimension_longueur?: number;
  poids?: number;
  dimension_socle?: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  is_admin: boolean;
}
