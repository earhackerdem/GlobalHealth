"""Onboarding perfil: patient_profile, body_measurement, family_history

onboarding-perfil design.md (Decision 2): three NEW tables, zero changes to
existing ones (additive-only migration). Sensitive columns (birth_date, sex,
allergies, value, other_text, relatives, note) store Fernet tokens written
by EncryptedString, so they are plain String here; the onboarding state and
the type/condition discriminators stay in the clear. relatives is a JSON
array serialized inside its encrypted column. No backfill (Migration Plan):
existing accounts get their profile row created pending on first access.

Revision ID: d5f2a8c41e07
Revises: c91f3b7a52e8
Create Date: 2026-10-19 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd5f2a8c41e07'
down_revision = 'c91f3b7a52e8'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('patient_profile',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('birth_date', sa.String(), nullable=True),
    sa.Column('sex', sa.String(), nullable=True),
    sa.Column('allergies', sa.String(), nullable=True),
    sa.Column('onboarding_outcome', sa.String(length=16), nullable=False),
    sa.Column('onboarding_closed_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id')
    )
    op.create_table('body_measurement',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('type', sa.String(length=16), nullable=False),
    sa.Column('value', sa.String(), nullable=False),
    sa.Column('measured_on', sa.Date(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('family_history',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('condition', sa.String(length=32), nullable=False),
    sa.Column('other_text', sa.String(), nullable=True),
    sa.Column('relatives', sa.String(), nullable=False),
    sa.Column('note', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('family_history')
    op.drop_table('body_measurement')
    op.drop_table('patient_profile')
