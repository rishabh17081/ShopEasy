"""add_subscription_id_column.py
Revision ID: 3a4b5c6d7e8f
Revises: add_card_number_column
Create Date: 2025-03-18 21:37:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '3a4b5c6d7e8f'
down_revision = 'add_card_number_column'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('cards', sa.Column('subscription_id', sa.String(100), nullable=True))

def downgrade():
    op.drop_column('cards', 'subscription_id')
