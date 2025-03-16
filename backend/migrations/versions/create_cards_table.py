"""Create cards table

Revision ID: 9e8b3f4a5d12
Revises: (use your previous migration id here)
Create Date: 2025-03-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '9e8b3f4a5d12'
down_revision = None  # Change this to your previous migration ID if you have one
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('cards',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('card_type', sa.String(length=50), nullable=True),
        sa.Column('last_four', sa.String(length=4), nullable=False),
        sa.Column('expiry_date', sa.String(length=7), nullable=False),
        sa.Column('cardholder_name', sa.String(length=100), nullable=False),
        sa.Column('is_default', sa.Boolean(), nullable=False, default=False),
        sa.Column('subscription_id', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.Index('idx_cards_user_id', 'user_id')
    )


def downgrade():
    op.drop_table('cards')
