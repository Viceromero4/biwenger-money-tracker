from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SeasonParticipant(Base):
    __tablename__ = "season_participants"

    __table_args__ = (
        UniqueConstraint(
            "season_id",
            "participant_id",
            name="uq_season_participants_season_id_participant_id",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    season_id: Mapped[int] = mapped_column(
        ForeignKey("seasons.id", ondelete="CASCADE"),
        nullable=False,
    )

    participant_id: Mapped[int] = mapped_column(
        ForeignKey("participants.id", ondelete="CASCADE"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    season: Mapped["Season"] = relationship(
        back_populates="participants",
    )

    participant: Mapped["Participant"] = relationship(
        back_populates="season_participations",
    )

    movements: Mapped[list["Movement"]] = relationship(
    back_populates="season_participant",
    cascade="all, delete-orphan",
)