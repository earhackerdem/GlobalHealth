"""Encrypt HealthRecordStub.note at rest

NFR-001 (approved review finding H7): health data must be encrypted at rest.
The ``note`` column becomes an unbounded VARCHAR holding a Fernet token
(app/core/encrypted.EncryptedString, same mechanism as OAuthIdentity.subject)
and the existing rows are encrypted in place. These are dev stub rows (few),
so the per-row Python loop is fine.

Revision ID: a7f3c9e21d54
Revises: c4e52a1b8d36
Create Date: 2026-10-11 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

from app.core.encrypted import EncryptedString, decrypt_str


# revision identifiers, used by Alembic.
revision = 'a7f3c9e21d54'
down_revision = 'c4e52a1b8d36'
branch_labels = None
depends_on = None


def upgrade():
    # Fernet tokens are longer than the plaintext: drop the length bound.
    op.alter_column(
        'healthrecordstub',
        'note',
        existing_type=sa.String(length=255),
        type_=sa.String(),
        existing_nullable=False,
    )
    bind = op.get_bind()
    column_type = EncryptedString()
    rows = bind.execute(sa.text('SELECT id, note FROM healthrecordstub')).all()
    for row_id, note in rows:
        if note is None or decrypt_str(str(note)) is not None:
            # Already a valid token for the current keys: idempotent re-run.
            continue
        bind.execute(
            sa.text('UPDATE healthrecordstub SET note = :note WHERE id = :id'),
            {'note': column_type.process_bind_param(str(note), bind.dialect), 'id': row_id},
        )


def downgrade():
    bind = op.get_bind()
    rows = bind.execute(sa.text('SELECT id, note FROM healthrecordstub')).all()
    for row_id, note in rows:
        if note is None:
            continue
        plaintext = decrypt_str(str(note))
        if plaintext is None:
            continue
        bind.execute(
            sa.text('UPDATE healthrecordstub SET note = :note WHERE id = :id'),
            {'note': plaintext[:255], 'id': row_id},
        )
    op.alter_column(
        'healthrecordstub',
        'note',
        existing_type=sa.String(),
        type_=sa.String(length=255),
        existing_nullable=False,
    )
