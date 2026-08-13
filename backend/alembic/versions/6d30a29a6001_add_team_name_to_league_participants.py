"""add team name to league participants

Revision ID: 6d30a29a6001
Revises: 169cd57b093e
Create Date: 2026-08-13
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6d30a29a6001"
down_revision: Union[str, Sequence[str], None] = "169cd57b093e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "league_participants",
        sa.Column(
            "team_name",
            sa.String(length=150),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "league_participants",
        "team_name",
    )