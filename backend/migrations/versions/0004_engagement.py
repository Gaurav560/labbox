"""Engagement: user_profile, the xp_event ledger, and daily drill answers.

Every user that exists now gets a profile marked as onboarded (they have used LabBox
already) and not yet backfilled: their earlier progress becomes XP on first use.

Revision ID: 0004
Revises: 0003
"""
import sqlalchemy as sa
import sqlmodel
from alembic import op


revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('drill_answer',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('day', sa.Date(), nullable=False),
    sa.Column('drill_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('choice', sa.Integer(), nullable=False),
    sa.Column('correct', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('drill_answer', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_drill_answer_user_id'), ['user_id'], unique=False)

    op.create_table('user_profile',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('display_name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('timezone', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('goal', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('placement_level', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('onboarded_at', sa.DateTime(), nullable=True),
    sa.Column('level', sa.Integer(), nullable=False),
    sa.Column('xp_total', sa.Integer(), nullable=False),
    sa.Column('streak_current', sa.Integer(), nullable=False),
    sa.Column('streak_best', sa.Integer(), nullable=False),
    sa.Column('last_active_day', sa.Date(), nullable=True),
    sa.Column('backfilled_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_table('xp_event',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('kind', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.Column('ref', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('day', sa.Date(), nullable=False),
    sa.Column('lab_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('chapter_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('task_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'ref')
    )
    with op.batch_alter_table('xp_event', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_xp_event_user_id'), ['user_id'], unique=False)
    # Existing users: onboarded, earlier progress still to be turned into XP (backfilled_at NULL).
    op.execute(
        'INSERT INTO user_profile (user_id, level, xp_total, streak_current, streak_best, onboarded_at, created_at) '
        'SELECT id, 1, 0, 0, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP FROM "user"'
    )



def downgrade() -> None:
    raise NotImplementedError("Migrations are additive only; restore a backup instead of downgrading")
