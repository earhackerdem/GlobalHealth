"""Snake case table names

tablas-snake-case (D25): the five tables that took SQLModel's default name
(cls.__name__.lower()) get a snake_case name, and so do their constraints
(pkey, fkey and Postgres 18's named NOT NULL) and their ix_ indexes, so no
name keeps the old prefix. The constraint and index names are read from the
catalog, not hard-coded: which ones exist depends on the Postgres version
(design.md, Decision 1). A rename only touches the catalog: rows stay put.

Revision ID: c4a9e1d7b2f5
Revises: 26de7399b12f
Create Date: 2026-10-31 00:00:00.000000

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = 'c4a9e1d7b2f5'
down_revision = '26de7399b12f'
branch_labels = None
depends_on = None


# (old, new). Each pass reads only that table's names and matches "<old>_",
# so healthrecord never touches healthrecordmedicine's and the order does not
# matter (review F5).
RENAMES = [
    ('healthrecordmedicine', 'health_record_medicine'),
    ('healthrecordattachment', 'health_record_attachment'),
    ('healthrecord', 'health_record'),
    ('consentgrant', 'consent_grant'),
    ('oauthidentity', 'oauth_identity'),
]


def _renamed(name, prefixes):
    for old, new in prefixes:
        if name.startswith(old):
            return new + name[len(old):]
    return None


def _rename_table(old, new):
    op.rename_table(old, new)
    bind = op.get_bind()
    quote = bind.dialect.identifier_preparer.quote_identifier

    # Constraints first: renaming a pkey (or unique) constraint renames its
    # index too, so the index pass below only sees what is left.
    constraints = bind.execute(
        sa.text(
            "SELECT c.conname FROM pg_constraint c "
            "JOIN pg_class t ON t.oid = c.conrelid "
            "JOIN pg_namespace n ON n.oid = t.relnamespace "
            "WHERE n.nspname = 'public' AND t.relname = :table "
            "ORDER BY c.conname"
        ),
        {'table': new},
    ).scalars().all()
    for name in constraints:
        target = _renamed(name, [(f'{old}_', f'{new}_')])
        if target is not None:
            op.execute(
                f'ALTER TABLE public.{quote(new)} '
                f'RENAME CONSTRAINT {quote(name)} TO {quote(target)}'
            )

    indexes = bind.execute(
        sa.text(
            "SELECT indexname FROM pg_indexes "
            "WHERE schemaname = 'public' AND tablename = :table "
            "ORDER BY indexname"
        ),
        {'table': new},
    ).scalars().all()
    for name in indexes:
        target = _renamed(name, [(f'ix_{old}_', f'ix_{new}_'), (f'{old}_', f'{new}_')])
        if target is not None:
            op.execute(
                f'ALTER INDEX public.{quote(name)} RENAME TO {quote(target)}'
            )


def upgrade():
    for old, new in RENAMES:
        _rename_table(old, new)


def downgrade():
    # The exact reverse.
    for old, new in reversed(RENAMES):
        _rename_table(new, old)
