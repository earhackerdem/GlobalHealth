"""Add OAuthIdentity and nullable hashed_password on user

Revision ID: b3d41f0a9c27
Revises: fe56fa70289e
Create Date: 2026-10-11 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'b3d41f0a9c27'
down_revision = 'fe56fa70289e'
branch_labels = None
depends_on = None


def upgrade():
    # Accounts created via Google OIDC have no local password
    op.alter_column('user', 'hashed_password',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # subject is stored encrypted (app/core/encrypted.py EncryptedString),
    # plain String at the DB level holding the Fernet ciphertext
    op.create_table('oauthidentity',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('provider', sqlmodel.sql.sqltypes.AutoString(length=32), nullable=False),
    sa.Column('subject', sa.String(), nullable=False),
    sa.Column('email', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('oauthidentity')
    op.alter_column('user', 'hashed_password',
               existing_type=sa.VARCHAR(),
               nullable=False)
