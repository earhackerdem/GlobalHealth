"""Receta mexicana: medicines child table, archive flag, confirmation status

receta-mexicana design.md: a prescription carries medicines[] 1..N in the
new ``healthrecordmedicine`` table (name/dose/frequency/route are Fernet
tokens, position preserves capture order); ``healthrecord`` gains
``diagnosis`` (encrypted), ``archived`` and ``confirmation_status`` (flow
metadata, in the clear — Decision 3), ``title`` becomes nullable, and the
retired record-level ``dose``/``valid_from``/``valid_to`` are dropped.

Data migration (Decision 4, no user data destroyed):
- each existing prescription gets ONE medicine row (name = decrypted title,
  re-encrypted; dose = record-level dose, re-encrypted), its validity window
  is appended to ``notes`` as "Vigencia migrada: <valid_from> a <valid_to>"
  ("desde <valid_from>" / "hasta <valid_to>" when only one bound exists),
  and its ``title`` is set to NULL;
- each existing diagnosis gets ``confirmation_status = 'unconfirmed'``.

Downgrade recreates the dropped columns and, ONLY to satisfy the original
NOT NULL on ``title``, copies the first medicine's name back into the title
of each prescription; the rest of the medicines data (extra medicines,
frequency, route) is NOT restored, and the "Vigencia migrada" note is not
unfolded back into valid_from/valid_to.

Revision ID: c91f3b7a52e8
Revises: 0b7c5e1d94aa
Create Date: 2026-10-18 00:00:00.000000

"""
import uuid

from alembic import op
import sqlalchemy as sa

from app.core.encrypted import EncryptedString


# revision identifiers, used by Alembic.
revision = 'c91f3b7a52e8'
down_revision = '0b7c5e1d94aa'
branch_labels = None
depends_on = None


def _encrypt(bind, value):
    """Fernet token for a plaintext value (same MultiFernet as the ORM)."""
    return EncryptedString().process_bind_param(value, bind.dialect)


def _decrypt(bind, value):
    """Plaintext for a stored token, with the SAME MultiFernet as the ORM.

    InvalidToken propagates ON PURPOSE (review S2): with a wrong
    ENCRYPTION_KEY the upgrade must abort — the whole migration runs in one
    transaction, so Alembic rolls everything back — instead of silently
    writing None over every title/dose/note and destroying the data.
    """
    return EncryptedString().process_result_value(value, bind.dialect)


def upgrade():
    op.create_table('healthrecordmedicine',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('record_id', sa.Uuid(), nullable=False),
    sa.Column('position', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('dose', sa.String(), nullable=True),
    sa.Column('frequency', sa.String(), nullable=True),
    sa.Column('route', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['record_id'], ['healthrecord.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('healthrecord', sa.Column('diagnosis', sa.String(), nullable=True))
    op.add_column(
        'healthrecord',
        sa.Column(
            'archived', sa.Boolean(), nullable=False, server_default=sa.text('false')
        ),
    )
    op.add_column(
        'healthrecord',
        sa.Column(
            'confirmation_status',
            sa.String(length=32),
            nullable=True,
        ),
    )
    op.alter_column(
        'healthrecord', 'title', existing_type=sa.String(), nullable=True
    )

    bind = op.get_bind()
    rows = bind.execute(
        sa.text(
            'SELECT id, record_type, title, notes, dose, valid_from, valid_to '
            'FROM healthrecord'
        )
    ).all()
    for row_id, record_type, title, notes, dose, valid_from, valid_to in rows:
        if record_type == 'diagnosis':
            bind.execute(
                sa.text(
                    "UPDATE healthrecord SET confirmation_status = 'unconfirmed' "
                    'WHERE id = :id'
                ),
                {'id': row_id},
            )
            continue
        # Prescription: fold title+dose into ONE medicine (re-encrypted) and
        # preserve the validity window inside notes.
        name_plain = _decrypt(bind, title)
        dose_plain = _decrypt(bind, dose)
        bind.execute(
            sa.text(
                'INSERT INTO healthrecordmedicine '
                '(id, record_id, position, name, dose, frequency, route) '
                'VALUES (:id, :record_id, 0, :name, :dose, NULL, NULL)'
            ),
            {
                'id': uuid.uuid4(),
                'record_id': row_id,
                'name': _encrypt(bind, name_plain or ''),
                'dose': _encrypt(bind, dose_plain) if dose_plain else None,
            },
        )
        new_notes = None
        if valid_from is not None or valid_to is not None:
            # Review K1: never print a bound that does not exist ("… a None").
            if valid_from is not None and valid_to is not None:
                legacy_note = f'Vigencia migrada: {valid_from} a {valid_to}'
            elif valid_from is not None:
                legacy_note = f'Vigencia migrada: desde {valid_from}'
            else:
                legacy_note = f'Vigencia migrada: hasta {valid_to}'
            notes_plain = _decrypt(bind, notes)
            folded = f'{notes_plain}\n{legacy_note}' if notes_plain else legacy_note
            new_notes = _encrypt(bind, folded)
        bind.execute(
            sa.text(
                'UPDATE healthrecord SET title = NULL, '
                'notes = COALESCE(:notes, notes) WHERE id = :id'
            ),
            {'id': row_id, 'notes': new_notes},
        )

    op.drop_column('healthrecord', 'dose')
    op.drop_column('healthrecord', 'valid_from')
    op.drop_column('healthrecord', 'valid_to')


def downgrade():
    op.add_column('healthrecord', sa.Column('dose', sa.String(), nullable=True))
    op.add_column('healthrecord', sa.Column('valid_from', sa.Date(), nullable=True))
    op.add_column('healthrecord', sa.Column('valid_to', sa.Date(), nullable=True))

    # Restore a NOT NULL-able title for prescriptions from their FIRST
    # medicine (name only); every other medicine datum is lost by design.
    bind = op.get_bind()
    rows = bind.execute(
        sa.text(
            'SELECT DISTINCT ON (record_id) record_id, name, dose '
            'FROM healthrecordmedicine ORDER BY record_id, position'
        )
    ).all()
    for record_id, name, dose in rows:
        bind.execute(
            sa.text(
                'UPDATE healthrecord SET title = :title, dose = :dose '
                'WHERE id = :id AND title IS NULL'
            ),
            {'id': record_id, 'title': name, 'dose': dose},
        )
    # Any prescription left without medicines (should not exist) still needs
    # a non-null title to satisfy the restored constraint.
    bind.execute(
        sa.text(
            'UPDATE healthrecord SET title = :placeholder WHERE title IS NULL'
        ),
        {'placeholder': _encrypt(bind, 'Receta migrada')},
    )
    op.alter_column(
        'healthrecord', 'title', existing_type=sa.String(), nullable=False
    )

    op.drop_column('healthrecord', 'confirmation_status')
    op.drop_column('healthrecord', 'archived')
    op.drop_column('healthrecord', 'diagnosis')
    op.drop_table('healthrecordmedicine')
