from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LeagueCreate(BaseModel):
    season_id: int
    name: str
    initial_balance: int


class LeagueUpdateBiwenger(BaseModel):
    biwenger_league_id: int | None


class LeagueUpdateSyncFrom(BaseModel):
    sync_from: datetime | None


class LeagueResponse(BaseModel):
    id: int
    season_id: int
    name: str
    initial_balance: int
    biwenger_league_id: int | None
    sync_from: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)