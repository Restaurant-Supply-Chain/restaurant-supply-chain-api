"""create RBAC tables

Revision ID: 0003_rbac
Revises: 0002_refresh_tokens
"""
from alembic import op
import sqlalchemy as sa


revision = '0003_rbac'
down_revision = '0002_refresh_tokens'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('permissions',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=80), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_table('roles',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=80), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_table('role_permissions',
        sa.Column('role_id', sa.BigInteger(), nullable=False),
        sa.Column('permission_id', sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('role_id', 'permission_id')
    )
    op.create_table('user_roles',
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('role_id', sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'role_id')
    )
    # Seed the six roles defined in the project requirements.
    roles = sa.table("roles", sa.column("name", sa.String(80)))
    op.bulk_insert(roles, [
        {"name": "PLATFORM_ADMIN"},
        {"name": "RESTAURANT_ADMIN"},
        {"name": "RESTAURANT_STAFF"},
        {"name": "SUPPLIER_ADMIN"},
        {"name": "SUPPLIER_STAFF"},
        {"name": "DRIVER"},
    ])


def downgrade():
    op.drop_table('user_roles')
    op.drop_table('role_permissions')
    op.drop_table('roles')
    op.drop_table('permissions')
