"""Create cards table

Revision ID: create_cards_table
Revises: 
Create Date: 2025-03-18 03:05:33.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'create_cards_table'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('cards',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('card_type', sa.String(length=50), nullable=False),
        sa.Column('last_four', sa.String(length=4), nullable=False),
        sa.Column('expiry_date', sa.String(length=7), nullable=False),
        sa.Column('cardholder_name', sa.String(length=100), nullable=False),
        sa.Column('is_default', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('cards')
