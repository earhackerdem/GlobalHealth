"""Add HealthRecordAttachment

Attachments of a clinical record (expediente-registros design.md §Interface
contract, ADR D16): filename (Fernet token) and content (Fernet token bytes
in bytea) encrypted at rest; media_type and size_bytes of the original in
the clear. Deleting the record cascades over its attachment rows.

Revision ID: 0b7c5e1d94aa
Revises: f8b2d6c47a19
Create Date: 2026-10-12 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '0b7c5e1d94aa'
down_revision = 'f8b2d6c47a19'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('healthrecordattachment',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('record_id', sa.Uuid(), nullable=False),
    sa.Column('filename', sa.String(), nullable=False),
    sa.Column('media_type', sqlmodel.sql.sqltypes.AutoString(length=64), nullable=False),
    sa.Column('size_bytes', sa.Integer(), nullable=False),
    sa.Column('content', sa.LargeBinary(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['record_id'], ['healthrecord.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('healthrecordattachment')
