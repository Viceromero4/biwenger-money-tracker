"""add movement operation type

Revision ID: 169cd57b093e
Revises: c3be6983fc21
Create Date: 2026-08-13 13:47:22.403416

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '169cd57b093e'
down_revision: Union[str, Sequence[str], None] = 'c3be6983fc21'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""

    movement_operation_type = sa.Enum(
        'CLAUSE',
        'PARTICIPANT_TRANSFER',
        'LOAN',
        name='movement_operation_type',
    )

    movement_operation_type.create(
        op.get_bind(),
        checkfirst=True,
    )

    op.add_column(
        'movements',
        sa.Column(
            'operation_type',
            movement_operation_type,
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column(
        'movements',
        'operation_type',
    )

    movement_operation_type = sa.Enum(
        'CLAUSE',
        'PARTICIPANT_TRANSFER',
        'LOAN',
        name='movement_operation_type',
    )

    movement_operation_type.drop(
        op.get_bind(),
        checkfirst=True,
    )