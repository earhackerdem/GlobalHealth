"""Add ConsentGrant and HealthRecordStub

ConsentGrant keeps consent as data, not as a flag: one row per grant with
version, sha256 of the exact text accepted, timestamp and auth method
(NFR-004). HealthRecordStub is the minimal router-of-proof table that E2
replaces with the real clinical records.

Revision ID: c4e52a1b8d36
Revises: b3d41f0a9c27
Create Date: 2026-10-11 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'c4e52a1b8d36'
down_revision = 'b3d41f0a9c27'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('consentgrant',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('version', sqlmodel.sql.sqltypes.AutoString(length=32), nullable=False),
    sa.Column('text_sha256', sqlmodel.sql.sqltypes.AutoString(length=64), nullable=False),
    sa.Column('granted_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('auth_method', sqlmodel.sql.sqltypes.AutoString(length=32), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('healthrecordstub',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('note', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
    sa.Column('owner_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('healthrecordstub')
    op.drop_table('consentgrant')
