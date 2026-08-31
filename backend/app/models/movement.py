from datetime import datetime
from enum import Enum


from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class MovementType(str, Enum):
    PURCHASE = "purchase"
    SALE = "sale"
    BONUS = "bonus"
    ROUND_BONUS = "round_bonus"
    CLAUSE_COMPENSATION = "clause_compensation"
    ADJUSTMENT = "adjustment"


class MovementOperationType(str, Enum):
    CLAUSE = "clause"
    PARTICIPANT_TRANSFER = "participant_transfer"
    LOAN = "loan"
    LOAN_RETURN = "loan_return"


class Movement(Base):
    __tablename__ = "movements"

    id: Mapped[int] = mapped_column(primary_key=True)

    league_participant_id: Mapped[int] = mapped_column(
        ForeignKey("league_participants.id", ondelete="CASCADE"),
        nullable=False,
    )

    type: Mapped[MovementType] = mapped_column(
        SqlEnum(
            MovementType,
            name="movement_type",
        ),
        nullable=False,
    )

    operation_type: Mapped[MovementOperationType | None] = mapped_column(
        SqlEnum(
            MovementOperationType,
            name="movement_operation_type",
        ),
        nullable=True,
    )

    amount: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    player_name: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    round_number: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    external_key: Mapped[str | None] = mapped_column(
    String(64),
    nullable=True,
    unique=True,
    )

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    league_participant: Mapped["LeagueParticipant"] = relationship(
        back_populates="movements",
    )