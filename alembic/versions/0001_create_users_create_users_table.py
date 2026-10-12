"""create users table

Revision ID: 0001_create_users
Revises:
"""
from alembic import op
import sqlalchemy as sa


revision = '0001_create_users'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('users',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('uuid', sa.CHAR(length=36), nullable=False),
        sa.Column('email', sa.String(length=254), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=120), nullable=False),
        sa.Column('role', sa.Enum('PLATFORM_ADMIN', 'RESTAURANT_ADMIN', 'RESTAURANT_STAFF', 'SUPPLIER_ADMIN', 'SUPPLIER_STAFF', 'DRIVER', name='user_role'), nullable=False),
        sa.Column('status', sa.Enum('ACTIVE', 'INACTIVE', 'SUSPENDED', 'PENDING', name='user_status'), server_default='PENDING', nullable=False),
        sa.Column('email_verified', sa.Boolean(), server_default=sa.text('0'), nullable=False),
        sa.Column('phone_verified', sa.Boolean(), server_default=sa.text('0'), nullable=False),
        sa.Column('last_login_at', sa.DateTime(), nullable=True),
        sa.Column('failed_login_count', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('locked_until', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('phone'),
        sa.UniqueConstraint('uuid')
    )


def downgrade():
    op.drop_table('users')
