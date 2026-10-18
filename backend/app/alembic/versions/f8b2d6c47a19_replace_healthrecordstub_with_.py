"""Replace HealthRecordStub with HealthRecord

The real clinical record book (expediente-registros design.md §Interface
contract): one table discriminated by record_type, clinical text columns
holding Fernet tokens (EncryptedString), type/dates/ids in the clear.
The stub rows are development scaffolding and are dropped with the table
(documented in evidence.md).

Revision ID: f8b2d6c47a19
Revises: a7f3c9e21d54
Create Date: 2026-10-12 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'f8b2d6c47a19'
down_revision = 'a7f3c9e21d54'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('healthrecord',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('owner_id', sa.Uuid(), nullable=False),
    sa.Column('record_type', sqlmodel.sql.sqltypes.AutoString(length=32), nullable=False),
    sa.Column('occurred_on', sa.Date(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('professional', sa.String(), nullable=True),
    sa.Column('notes', sa.String(), nullable=True),
    sa.Column('dose', sa.String(), nullable=True),
    sa.Column('valid_from', sa.Date(), nullable=True),
    sa.Column('valid_to', sa.Date(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('healthrecordstub')


def downgrade():
    op.create_table('healthrecordstub',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('note', sa.String(), nullable=False),
    sa.Column('owner_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('healthrecord')
