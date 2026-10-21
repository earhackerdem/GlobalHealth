"""Perfil hábitos: patient_profile.habits

perfil-habitos design.md (Decision 1, Migration Plan): additive only.
patient_profile gains one NULLABLE encrypted column, habits, holding a Fernet
token of the normalized questionnaire's JSON written by EncryptedString, so it
is a plain String here (like blood_type/sections_none). No backfill; downgrade
drops exactly what upgrade added.

Revision ID: 7d3e9a1c5b42
Revises: 2c7fa6505d5c
Create Date: 2026-10-20 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7d3e9a1c5b42'
down_revision = '2c7fa6505d5c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('patient_profile', sa.Column('habits', sa.String(), nullable=True))


def downgrade():
    op.drop_column('patient_profile', 'habits')
