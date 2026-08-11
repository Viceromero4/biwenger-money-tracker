from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LeagueCreate(BaseModel):
    season_id: int
    name: str
    initial_balance: int


class LeagueResponse(BaseModel):
    id: int
    season_id: int
    name: str
    initial_balance: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)