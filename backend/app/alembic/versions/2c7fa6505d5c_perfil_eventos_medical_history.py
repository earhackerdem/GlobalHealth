"""Perfil eventos: medical_history_entry + blood_type/sections_none

perfil-eventos design.md (Decisions 1-3, Migration Plan): additive only. One
NEW table, medical_history_entry, whose content column holds a Fernet token
of the entry's JSON (its section included) written by EncryptedString, so it
is a plain String here; only id, user_id and created_at stay in the clear.
patient_profile gains two NULLABLE encrypted columns: blood_type and
sections_none (a JSON list serialized inside the token). No backfill;
downgrade drops exactly what upgrade added.

Revision ID: 2c7fa6505d5c
Revises: f4b2c7d81e93
Create Date: 2026-10-20 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2c7fa6505d5c'
down_revision = 'f4b2c7d81e93'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('medical_history_entry',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('content', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('patient_profile', sa.Column('blood_type', sa.String(), nullable=True))
    op.add_column('patient_profile', sa.Column('sections_none', sa.String(), nullable=True))


def downgrade():
    op.drop_column('patient_profile', 'sections_none')
    op.drop_column('patient_profile', 'blood_type')
    op.drop_table('medical_history_entry')
