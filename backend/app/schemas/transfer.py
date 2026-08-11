from datetime import datetime

from pydantic import BaseModel, model_validator


class PlayerTransferCreate(BaseModel):
    buyer_league_participant_id: int
    seller_league_participant_id: int
    amount: int
    player_name: str
    occurred_at: datetime
    description: str | None = None

    @model_validator(mode="after")
    def validate_transfer(self):
        if self.amount <= 0:
            raise ValueError("Transfer amount must be greater than zero")

        if (
            self.buyer_league_participant_id
            == self.seller_league_participant_id
        ):
            raise ValueError(
                "Buyer and seller must be different participants"
            )

        if not self.player_name.strip():
            raise ValueError("Player name is required")

        return self