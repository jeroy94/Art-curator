# Système de Gestion d'Exposition d'Art

Application web permettant la gestion des soumissions d'œuvres d'art, leur sélection et leur visualisation en 3D.

## Fonctionnalités

- Soumission d'œuvres d'art par les artistes
- Système de vote pour la sélection des œuvres
- Génération de PDF pour les artistes
- Visualisation 3D des œuvres
- Gestion des différents types d'œuvres (peintures, sculptures, etc.)
- Affichage optimisé des images avec dimensions standardisées (300x200px)
- Visualisation des images en grand format via modal interactif
- Interface responsive avec Bootstrap

## Interface Utilisateur

### Affichage des Images
- Les images sont affichées dans des conteneurs standardisés de 300x200px
- Préservation des proportions des images grâce à object-fit: contain
- Fond gris clair pour une meilleure visibilité
- Images centrées dans leur conteneur

### Fonctionnalités Interactives
- Dans la liste des œuvres, les images sont cliquables
- Ouverture d'un modal Bootstrap pour afficher l'image en grand format
- Navigation intuitive avec fermeture du modal via bouton ou clic extérieur
- Titre de l'œuvre affiché dans le modal

## Installation

1. Créer un environnement virtuel Python :
```bash
python -m venv venv
.\venv\Scripts\activate
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Configurer les variables d'environnement :
Créer un fichier `.env` à la racine du projet avec :
```
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=votre_clé_secrète
DATABASE_URL=sqlite:///art_database.db
```

4. Initialiser la base de données :
```bash
flask db init
flask db migrate
flask db upgrade
```

5. Lancer l'application :
```bash
flask run
```

## Structure du Projet

```
image_to_3d/
├── app/
│   ├── models/
│   ├── routes/
│   ├── static/
│   └── templates/
│       └── artworks/
│           ├── list.html      # Liste des œuvres avec modal pour les images
│           └── selected.html  # Affichage des œuvres sélectionnées
├── migrations/
├── venv/
├── .env
├── app.py
├── config.py
└── requirements.txt
```

## Utilisation

1. Les artistes peuvent soumettre leurs œuvres via le formulaire en ligne
2. Les administrateurs peuvent voter et sélectionner les œuvres
3. Génération automatique des PDF pour les artistes sélectionnés
4. Visualisation 3D des œuvres disponible pour chaque pièce
5. Cliquer sur une image dans la liste pour l'afficher en grand format
