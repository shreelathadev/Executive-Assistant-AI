"""add task_checkins table

Revision ID: cf1596fdc127
Revises: 1337cab1aeb5
Create Date: 2026-09-14 19:43:31.158525

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cf1596fdc127'
down_revision: Union[str, Sequence[str], None] = '1337cab1aeb5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'task_checkins',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('frequency', sa.String(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('check_in_date', sa.Date(), nullable=False),
        sa.Column('completed', sa.Boolean(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('responded_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], name=op.f('fk_task_checkins_task_id_tasks'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_task_checkins_user_id_users')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_task_checkins')),
    )
    op.create_index(op.f('ix_task_checkins_id'), 'task_checkins', ['id'], unique=False)
    op.create_index(op.f('ix_task_checkins_task_id'), 'task_checkins', ['task_id'], unique=False)
    op.create_index(op.f('ix_task_checkins_user_id'), 'task_checkins', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_task_checkins_user_id'), table_name='task_checkins')
    op.drop_index(op.f('ix_task_checkins_task_id'), table_name='task_checkins')
    op.drop_index(op.f('ix_task_checkins_id'), table_name='task_checkins')
    op.drop_table('task_checkins')

