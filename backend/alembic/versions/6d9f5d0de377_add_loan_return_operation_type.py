"""add loan return operation type

Revision ID: 6d9f5d0de377
Revises: acf95ccb42b8
Create Date: 2026-08-31 18:21:39.876259

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6d9f5d0de377'
down_revision: Union[str, Sequence[str], None] = 'acf95ccb42b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        "ALTER TYPE movement_operation_type "
        "ADD VALUE IF NOT EXISTS 'LOAN_RETURN'"
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
