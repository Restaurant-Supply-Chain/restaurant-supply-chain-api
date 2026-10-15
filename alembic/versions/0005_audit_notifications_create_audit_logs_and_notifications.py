"""create audit logs and notifications

Revision ID: 0005_audit_notifications
Revises: 0004_password_resets
"""
from alembic import op
import sqlalchemy as sa


revision = '0005_audit_notifications'
down_revision = '0004_password_resets'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('audit_logs',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('actor_id', sa.BigInteger(), nullable=True),
        sa.Column('action', sa.String(length=80), nullable=False),
        sa.Column('entity', sa.String(length=80), nullable=False),
        sa.Column('entity_id', sa.BigInteger(), nullable=True),
        sa.Column('before_json', sa.JSON(none_as_null=True), nullable=True),
        sa.Column('after_json', sa.JSON(none_as_null=True), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['actor_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_logs_actor_id'), 'audit_logs', ['actor_id'], unique=False)
    op.create_table('notifications',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('type', sa.String(length=80), nullable=False),
        sa.Column('title', sa.String(length=120), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('payload_json', sa.JSON(none_as_null=True), nullable=True),
        sa.Column('channel', sa.String(length=20), server_default='IN_APP', nullable=False),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notifications_user_id'), 'notifications', ['user_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_notifications_user_id'), table_name='notifications')
    op.drop_table('notifications')
    op.drop_index(op.f('ix_audit_logs_actor_id'), table_name='audit_logs')
    op.drop_table('audit_logs')
