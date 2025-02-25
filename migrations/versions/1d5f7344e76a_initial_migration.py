"""Initial migration

Revision ID: 1d5f7344e76a
Revises: 
Create Date: 2025-02-25 16:46:06.301849

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1d5f7344e76a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('artworks')
    op.drop_table('artists')
    op.drop_table('users')
    op.drop_table('votes')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('votes',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('artwork_id', sa.INTEGER(), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.Column('vote_type', sa.VARCHAR(length=10), nullable=False),
    sa.Column('vote_date', sa.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['artwork_id'], ['artworks.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('username', sa.VARCHAR(length=80), nullable=False),
    sa.Column('email', sa.VARCHAR(length=120), nullable=False),
    sa.Column('password_hash', sa.VARCHAR(length=128), nullable=True),
    sa.Column('is_admin', sa.BOOLEAN(), nullable=True),
    sa.Column('created_at', sa.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('artists',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('numero_dossier', sa.VARCHAR(length=50), nullable=True),
    sa.Column('civilite', sa.VARCHAR(length=10), nullable=True),
    sa.Column('nom', sa.VARCHAR(length=100), nullable=False),
    sa.Column('prenom', sa.VARCHAR(length=100), nullable=False),
    sa.Column('nom_artiste', sa.VARCHAR(length=100), nullable=True),
    sa.Column('prenom_artiste', sa.VARCHAR(length=100), nullable=True),
    sa.Column('adresse', sa.VARCHAR(length=200), nullable=True),
    sa.Column('code_postal', sa.VARCHAR(length=10), nullable=True),
    sa.Column('ville', sa.VARCHAR(length=100), nullable=True),
    sa.Column('pays', sa.VARCHAR(length=100), nullable=True),
    sa.Column('telephone', sa.VARCHAR(length=20), nullable=True),
    sa.Column('email', sa.VARCHAR(length=120), nullable=False),
    sa.Column('site_internet', sa.VARCHAR(length=200), nullable=True),
    sa.Column('facebook', sa.VARCHAR(length=200), nullable=True),
    sa.Column('numero_mda', sa.VARCHAR(length=50), nullable=True),
    sa.Column('numero_siret', sa.VARCHAR(length=50), nullable=True),
    sa.Column('categorie', sa.VARCHAR(length=50), nullable=True),
    sa.Column('edition_adresse', sa.BOOLEAN(), nullable=True),
    sa.Column('edition_telephone', sa.BOOLEAN(), nullable=True),
    sa.Column('edition_email', sa.BOOLEAN(), nullable=True),
    sa.Column('edition_site', sa.BOOLEAN(), nullable=True),
    sa.Column('edition_facebook', sa.BOOLEAN(), nullable=True),
    sa.Column('nom_catalogue', sa.VARCHAR(length=200), nullable=True),
    sa.Column('created_at', sa.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('numero_dossier')
    )
    op.create_table('artworks',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('artist_id', sa.INTEGER(), nullable=False),
    sa.Column('numero', sa.VARCHAR(length=50), nullable=True),
    sa.Column('titre', sa.VARCHAR(length=200), nullable=False),
    sa.Column('description', sa.TEXT(), nullable=True),
    sa.Column('technique', sa.VARCHAR(length=200), nullable=True),
    sa.Column('materiaux', sa.VARCHAR(length=200), nullable=True),
    sa.Column('annee_creation', sa.INTEGER(), nullable=True),
    sa.Column('dimension_largeur', sa.FLOAT(), nullable=True),
    sa.Column('dimension_hauteur', sa.FLOAT(), nullable=True),
    sa.Column('dimension_profondeur', sa.FLOAT(), nullable=True),
    sa.Column('cadre_largeur', sa.FLOAT(), nullable=True),
    sa.Column('cadre_hauteur', sa.FLOAT(), nullable=True),
    sa.Column('cadre_profondeur', sa.FLOAT(), nullable=True),
    sa.Column('prix', sa.FLOAT(), nullable=True),
    sa.Column('photo_path', sa.VARCHAR(length=200), nullable=True),
    sa.Column('model3d_path', sa.VARCHAR(length=200), nullable=True),
    sa.Column('created_at', sa.DATETIME(), nullable=True),
    sa.Column('statut', sa.VARCHAR(length=20), nullable=True),
    sa.ForeignKeyConstraint(['artist_id'], ['artists.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('numero')
    )
    # ### end Alembic commands ###
