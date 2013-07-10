"""add price field to Listing table: attempt 2

Revision ID: 30f0c9b36d52
Revises: 3912836e4abf
Create Date: 2013-07-09 16:32:37.011604

"""

# revision identifiers, used by Alembic.
revision = '30f0c9b36d52'
down_revision = '3912836e4abf'

from alembic import op
import sqlalchemy as sa


def upgrade():
	op.drop_column('listing', 'price')

def downgrade():
	False
