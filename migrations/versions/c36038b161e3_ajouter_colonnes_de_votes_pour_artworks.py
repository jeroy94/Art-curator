"""Ajouter colonnes de votes pour artworks

Revision ID: c36038b161e3
Revises: 1d5f7344e76a
Create Date: 2025-02-26 08:55:17.691549

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c36038b161e3'
down_revision = '1d5f7344e76a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('artworks', schema=None) as batch_op:
        batch_op.add_column(sa.Column('up_votes_count', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('down_votes_count', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('artworks', schema=None) as batch_op:
        batch_op.drop_column('down_votes_count')
        batch_op.drop_column('up_votes_count')

    # ### end Alembic commands ###
