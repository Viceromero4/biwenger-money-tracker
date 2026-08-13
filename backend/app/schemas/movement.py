from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator

from app.models.movement import MovementType, MovementOperationType


class MovementCreate(BaseModel):
    league_participant_id: int
    type: MovementType
    amount: int
    player_name: str | None = None
    description: str | None = None
    occurred_at: datetime

    @model_validator(mode="after")
    def validate_movement(self):
        if self.amount == 0:
            raise ValueError("Amount cannot be zero")

        if self.type == MovementType.PURCHASE:
            if self.amount > 0:
                raise ValueError("Purchase amount must be negative")
            if not self.player_name:
                raise ValueError("Player name is required for purchases")

        if self.type == MovementType.SALE:
            if self.amount < 0:
                raise ValueError("Sale amount must be positive")
            if not self.player_name:
                raise ValueError("Player name is required for sales")

        if self.type == MovementType.BONUS:
            if self.amount < 0:
                raise ValueError("Bonus amount must be positive")

        if self.type == MovementType.CLAUSE_COMPENSATION:
            if self.amount < 0:
                raise ValueError("Clause compensation amount must be positive")
            if not self.player_name:
                raise ValueError(
                    "Player name is required for clause compensation"
                )

        if self.type == MovementType.ADJUSTMENT:
            if not self.description:
                raise ValueError("Description is required for adjustments")

        return self


class MovementResponse(BaseModel):
    id: int
    league_participant_id: int
    type: MovementType
    operation_type: MovementOperationType | None
    amount: int
    player_name: str | None
    description: str | None
    occurred_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
    