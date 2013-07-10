"""add price field to Listing table

Revision ID: 3912836e4abf
Revises: None
Create Date: 2013-07-09 16:09:39.103980

"""

# revision identifiers, used by Alembic.
revision = '3912836e4abf'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('listing', sa.Column('price', sa.String))


def downgrade():
    op.drop_column('listing', 'price')
