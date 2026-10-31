"""Index foreign keys

bd-candados-indices-y-log design.md (Decision 4): every foreign key gets an
index led by its column (ix_<table>_<column>), so the owner listings and the
ON DELETE CASCADE of an account search by index instead of scanning. Additive
only; downgrade drops exactly what upgrade added.

Revision ID: 26de7399b12f
Revises: 3b8e5f2a9c61
Create Date: 2026-10-31 00:00:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '26de7399b12f'
down_revision = '3b8e5f2a9c61'
branch_labels = None
depends_on = None


FOREIGN_KEYS = [
    ('healthrecord', 'owner_id'),
    ('healthrecordattachment', 'record_id'),
    ('healthrecordmedicine', 'record_id'),
    ('medical_history_entry', 'user_id'),
    ('family_history', 'user_id'),
    ('body_measurement', 'user_id'),
    ('consentgrant', 'user_id'),
    ('oauthidentity', 'user_id'),
    ('item', 'owner_id'),
]


def upgrade():
    # The tables are small today; a large one would need CREATE INDEX CONCURRENTLY.
    for table, column in FOREIGN_KEYS:
        op.create_index(op.f(f'ix_{table}_{column}'), table, [column])


def downgrade():
    for table, column in reversed(FOREIGN_KEYS):
        op.drop_index(op.f(f'ix_{table}_{column}'), table_name=table)
