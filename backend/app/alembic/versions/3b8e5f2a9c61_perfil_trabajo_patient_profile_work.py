"""Perfil trabajo: patient_profile.work

perfil-trabajo design.md (Decision 1, Migration Plan): additive only.
patient_profile gains one NULLABLE encrypted column, work, holding a Fernet
token of the normalized work block's JSON written by EncryptedString, so it is
a plain String here (like habits). No backfill; downgrade drops exactly what
upgrade added.

Revision ID: 3b8e5f2a9c61
Revises: 7d3e9a1c5b42
Create Date: 2026-10-29 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3b8e5f2a9c61'
down_revision = '7d3e9a1c5b42'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('patient_profile', sa.Column('work', sa.String(), nullable=True))


def downgrade():
    op.drop_column('patient_profile', 'work')
