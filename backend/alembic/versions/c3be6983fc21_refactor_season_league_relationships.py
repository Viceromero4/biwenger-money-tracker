"""refactor season league relationships

Revision ID: c3be6983fc21
Revises: 919fd02a25d4
Create Date: 2026-08-11 16:46:33.240718

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c3be6983fc21'
down_revision: Union[str, Sequence[str], None] = '919fd02a25d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Remove the FK from movements before removing season_participants
    op.drop_constraint(
        "movements_season_participant_id_fkey",
        "movements",
        type_="foreignkey",
    )

    # 2. Remove the old movement relation
    op.drop_column(
        "movements",
        "season_participant_id",
    )

    # 3. Remove the old participation table
    op.drop_table("season_participants")

    # 4. Refactor seasons:
    # Season no longer belongs to a league and no longer stores initial balance
    op.drop_constraint(
        "uq_seasons_league_id_name",
        "seasons",
        type_="unique",
    )

    op.drop_constraint(
        "seasons_league_id_fkey",
        "seasons",
        type_="foreignkey",
    )

    op.drop_column(
        "seasons",
        "initial_balance",
    )

    op.drop_column(
        "seasons",
        "league_id",
    )

    # Season names are unique
    op.create_unique_constraint(
        "uq_seasons_name",
        "seasons",
        ["name"],
    )

    # 5. Refactor leagues:
    # League now belongs to a season and stores the initial balance
    op.add_column(
        "leagues",
        sa.Column(
            "season_id",
            sa.Integer(),
            nullable=False,
        ),
    )

    op.add_column(
        "leagues",
        sa.Column(
            "initial_balance",
            sa.BigInteger(),
            nullable=False,
        ),
    )

    op.create_foreign_key(
        "leagues_season_id_fkey",
        "leagues",
        "seasons",
        ["season_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_unique_constraint(
        "uq_leagues_season_id_name",
        "leagues",
        ["season_id", "name"],
    )

    # 6. Create the new participation table
    op.create_table(
        "league_participants",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "league_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "participant_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["league_id"],
            ["leagues.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["participant_id"],
            ["participants.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "league_id",
            "participant_id",
            name="uq_league_participants_league_id_participant_id",
        ),
    )

    # 7. Connect movements to LeagueParticipant
    op.add_column(
        "movements",
        sa.Column(
            "league_participant_id",
            sa.Integer(),
            nullable=False,
        ),
    )

    op.create_foreign_key(
        "movements_league_participant_id_fkey",
        "movements",
        "league_participants",
        ["league_participant_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    # 1. Remove new movement relation
    op.drop_constraint(
        "movements_league_participant_id_fkey",
        "movements",
        type_="foreignkey",
    )

    op.drop_column(
        "movements",
        "league_participant_id",
    )

    # 2. Remove LeagueParticipant
    op.drop_table("league_participants")

    # 3. Restore leagues
    op.drop_constraint(
        "uq_leagues_season_id_name",
        "leagues",
        type_="unique",
    )

    op.drop_constraint(
        "leagues_season_id_fkey",
        "leagues",
        type_="foreignkey",
    )

    op.drop_column(
        "leagues",
        "initial_balance",
    )

    op.drop_column(
        "leagues",
        "season_id",
    )

    # 4. Restore seasons
    op.drop_constraint(
        "uq_seasons_name",
        "seasons",
        type_="unique",
    )

    op.add_column(
        "seasons",
        sa.Column(
            "league_id",
            sa.Integer(),
            nullable=False,
        ),
    )

    op.add_column(
        "seasons",
        sa.Column(
            "initial_balance",
            sa.BigInteger(),
            nullable=False,
        ),
    )

    op.create_foreign_key(
        "seasons_league_id_fkey",
        "seasons",
        "leagues",
        ["league_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_unique_constraint(
        "uq_seasons_league_id_name",
        "seasons",
        ["league_id", "name"],
    )

    # 5. Restore SeasonParticipant
    op.create_table(
        "season_participants",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "season_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "participant_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["season_id"],
            ["seasons.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["participant_id"],
            ["participants.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "season_id",
            "participant_id",
            name="uq_season_participants_season_id_participant_id",
        ),
    )

    # 6. Restore movement relation
    op.add_column(
        "movements",
        sa.Column(
            "season_participant_id",
            sa.Integer(),
            nullable=False,
        ),
    )

    op.create_foreign_key(
        "movements_season_participant_id_fkey",
        "movements",
        "season_participants",
        ["season_participant_id"],
        ["id"],
        ondelete="CASCADE",
    )