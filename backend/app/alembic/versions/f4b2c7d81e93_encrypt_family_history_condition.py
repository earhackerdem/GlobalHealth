"""Encrypt family_history.condition at rest

Review G2 (Saúl's call: the spec mandates encrypting the condition). The
``condition`` column becomes an unbounded VARCHAR holding a Fernet token
written by app/core/encrypted.EncryptedString (same precedent as
a7f3c9e21d54 / c91f3b7a52e8) and the existing rows are re-encrypted in place
with the SAME MultiFernet as the ORM. Additive-only: no column added or
dropped, no table touched beyond family_history. The whole migration runs in
ONE transaction; on downgrade a wrong ENCRYPTION_KEY makes InvalidToken
propagate ON PURPOSE (pattern c91f3b7a52e8) so Alembic rolls everything back
instead of silently destroying data. With condition encrypted, per-user
uniqueness cannot live in a partial index (Fernet is non-deterministic): the
route dedupes by decrypt-and-compare (review G3).

Revision ID: f4b2c7d81e93
Revises: d5f2a8c41e07
Create Date: 2026-10-19 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

from app.core.encrypted import EncryptedString, decrypt_str


# revision identifiers, used by Alembic.
revision = 'f4b2c7d81e93'
down_revision = 'd5f2a8c41e07'
branch_labels = None
depends_on = None


def upgrade():
    # Fernet tokens are longer than the plaintext: drop the length bound.
    op.alter_column(
        'family_history',
        'condition',
        existing_type=sa.String(length=32),
        type_=sa.String(),
        existing_nullable=False,
    )
    bind = op.get_bind()
    column_type = EncryptedString()
    rows = bind.execute(sa.text('SELECT id, condition FROM family_history')).all()
    for row_id, condition in rows:
        if decrypt_str(str(condition)) is not None:
            # Already a valid token for the current keys: idempotent re-run.
            continue
        bind.execute(
            sa.text(
                'UPDATE family_history SET condition = :condition WHERE id = :id'
            ),
            {
                'condition': column_type.process_bind_param(
                    str(condition), bind.dialect
                ),
                'id': row_id,
            },
        )


def downgrade():
    bind = op.get_bind()
    column_type = EncryptedString()
    rows = bind.execute(sa.text('SELECT id, condition FROM family_history')).all()
    for row_id, condition in rows:
        # InvalidToken propagates ON PURPOSE: with a wrong ENCRYPTION_KEY the
        # downgrade must abort (single transaction) instead of writing junk.
        plaintext = column_type.process_result_value(str(condition), bind.dialect)
        bind.execute(
            sa.text(
                'UPDATE family_history SET condition = :condition WHERE id = :id'
            ),
            {'condition': (plaintext or '')[:32], 'id': row_id},
        )
    op.alter_column(
        'family_history',
        'condition',
        existing_type=sa.String(),
        type_=sa.String(length=32),
        existing_nullable=False,
    )
