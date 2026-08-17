from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class League(Base):
    __tablename__ = "leagues"

    __table_args__ = (
        UniqueConstraint(
            "season_id",
            "name",
            name="uq_leagues_season_id_name",
        ),
        UniqueConstraint(
            "season_id",
            "biwenger_league_id",
            name="uq_leagues_season_id_biwenger_league_id",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    season_id: Mapped[int] = mapped_column(
        ForeignKey("seasons.id", ondelete="CASCADE"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    initial_balance: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    biwenger_league_id: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    sync_from: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    season: Mapped["Season"] = relationship(
        back_populates="leagues",
    )

    participants: Mapped[list["LeagueParticipant"]] = relationship(
        back_populates="league",
        cascade="all, delete-orphan",
    )