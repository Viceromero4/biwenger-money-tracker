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


class Season(Base):
    __tablename__ = "seasons"

    __table_args__ = (
        UniqueConstraint(
            "league_id",
            "name",
            name="uq_seasons_league_id_name",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    league_id: Mapped[int] = mapped_column(
        ForeignKey("leagues.id", ondelete="CASCADE"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    initial_balance: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    league: Mapped["League"] = relationship(
        back_populates="seasons",
    )
    
    participants: Mapped[list["SeasonParticipant"]] = relationship(
    back_populates="season",
    cascade="all, delete-orphan",
)