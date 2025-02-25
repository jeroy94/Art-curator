from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import os

class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        # Ajout de styles personnalisés
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Centré
        ))
        self.styles.add(ParagraphStyle(
            name='ArtworkTitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12
        ))

    def _format_dimensions(self, artwork):
        if artwork.type_oeuvre == 'Sculpture':
            return f"{artwork.dimension_hauteur}h x {artwork.dimension_largeur}l x {artwork.dimension_longueur}L cm"
        else:
            dimensions = []
            if artwork.dimension_hors_cadre_hauteur:
                dimensions.append(
                    f"Hors cadre: {artwork.dimension_hors_cadre_hauteur}h x {artwork.dimension_hors_cadre_largeur}l cm"
                )
            if artwork.dimension_avec_cadre_hauteur:
                dimensions.append(
                    f"Avec cadre: {artwork.dimension_avec_cadre_hauteur}h x {artwork.dimension_avec_cadre_largeur}l cm"
                )
            return " | ".join(dimensions)

    def generate_catalog(self, artworks, output_buffer):
        doc = SimpleDocTemplate(
            output_buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        # Préparation du contenu
        story = []

        # Titre du catalogue
        story.append(Paragraph("Catalogue des Œuvres Sélectionnées", self.styles['CustomTitle']))
        story.append(Spacer(1, 30))

        for artwork in artworks:
            # Conteneur pour l'image et les informations
            image_path = os.path.join('uploads', artwork.photo_path)
            if os.path.exists(image_path):
                img = Image(image_path, width=400, height=300)
                story.append(img)
                story.append(Spacer(1, 10))

            # Titre de l'œuvre
            story.append(Paragraph(artwork.nom, self.styles['ArtworkTitle']))

            # Informations de l'artiste et de l'œuvre
            info_data = [
                ['Artiste:', f"{artwork.artist.nom} {artwork.artist.prenom} ({artwork.artist.nom_artiste})"],
                ['Type:', artwork.type_oeuvre],
                ['Technique:', artwork.technique],
                ['Prix:', f"{artwork.prix} €"],
                ['Dimensions:', self._format_dimensions(artwork)]
            ]

            if artwork.type_oeuvre == 'Sculpture' and artwork.poids:
                info_data.append(['Poids:', f"{artwork.poids} kg"])

            # Création du tableau d'informations
            info_table = Table(
                info_data,
                colWidths=[100, 400],
                style=TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                ])
            )
            story.append(info_table)
            story.append(Spacer(1, 20))

            # Informations de contact
            contact_data = [
                ['Contact:', artwork.artist.email]
            ]
            if artwork.artist.telephone:
                contact_data.append(['Téléphone:', artwork.artist.telephone])

            contact_table = Table(
                contact_data,
                colWidths=[100, 400],
                style=TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.gray),
                ])
            )
            story.append(contact_table)
            story.append(Spacer(1, 30))

        # Génération du PDF
        doc.build(story)

    def generate_artist_summary(self, artist, artworks, output_buffer):
        doc = SimpleDocTemplate(
            output_buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        story = []

        # En-tête avec les informations de l'artiste
        story.append(Paragraph(f"Résumé des Œuvres - {artist.nom_artiste}", self.styles['CustomTitle']))
        
        artist_info = [
            ['Nom:', f"{artist.nom} {artist.prenom}"],
            ['Email:', artist.email]
        ]
        if artist.telephone:
            artist_info.append(['Téléphone:', artist.telephone])
        if artist.adresse:
            artist_info.append(['Adresse:', artist.adresse])

        artist_table = Table(
            artist_info,
            colWidths=[100, 400],
            style=TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
            ])
        )
        story.append(artist_table)
        story.append(Spacer(1, 30))

        # Liste des œuvres sélectionnées
        story.append(Paragraph("Œuvres Sélectionnées", self.styles['Heading2']))
        story.append(Spacer(1, 10))

        for artwork in artworks:
            if not artwork.selectionne:
                continue

            image_path = os.path.join('uploads', artwork.photo_path)
            if os.path.exists(image_path):
                img = Image(image_path, width=300, height=225)
                story.append(img)
                story.append(Spacer(1, 10))

            story.append(Paragraph(artwork.nom, self.styles['ArtworkTitle']))

            artwork_info = [
                ['Type:', artwork.type_oeuvre],
                ['Technique:', artwork.technique],
                ['Prix:', f"{artwork.prix} €"],
                ['Dimensions:', self._format_dimensions(artwork)]
            ]

            if artwork.type_oeuvre == 'Sculpture' and artwork.poids:
                artwork_info.append(['Poids:', f"{artwork.poids} kg"])

            artwork_table = Table(
                artwork_info,
                colWidths=[100, 400],
                style=TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                ])
            )
            story.append(artwork_table)
            story.append(Spacer(1, 20))

        # Génération du PDF
        doc.build(story)
