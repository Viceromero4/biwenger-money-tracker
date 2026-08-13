from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func

from app.db.base import Base


class LeagueParticipant(Base):
    __tablename__ = "league_participants"

    __table_args__ = (
        UniqueConstraint(
            "league_id",
            "participant_id",
            name="uq_league_participants_league_id_participant_id",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    league_id: Mapped[int] = mapped_column(
        ForeignKey("leagues.id", ondelete="CASCADE"),
        nullable=False,
    )

    participant_id: Mapped[int] = mapped_column(
        ForeignKey("participants.id", ondelete="CASCADE"),
        nullable=False,
    )

    team_name: Mapped[str | None] = mapped_column(
    String(150),
    nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    league: Mapped["League"] = relationship(
        back_populates="participants",
    )

    participant: Mapped["Participant"] = relationship(
        back_populates="league_participations",
    )

    movements: Mapped[list["Movement"]] = relationship(
        back_populates="league_participant",
        cascade="all, delete-orphan",
    )