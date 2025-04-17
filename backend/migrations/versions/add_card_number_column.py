"""Add card_number column to cards table

Revision ID: add_card_number_column
Revises: create_cards_table
Create Date: 2025-03-18 00:27:30.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_card_number_column'
down_revision = 'create_cards_table'
branch_labels = None
depends_on = None


def upgrade():
    # Add card_number column to cards table
    op.add_column('cards', sa.Column('card_number', sa.String(length=19), nullable=True))
    
    # Update existing records to have empty card_number
    op.execute("UPDATE cards SET card_number = '' WHERE card_number IS NULL")


def downgrade():
    # Remove card_number column from cards table
    op.drop_column('cards', 'card_number')
