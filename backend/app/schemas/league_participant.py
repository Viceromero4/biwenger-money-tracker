from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LeagueParticipantCreate(BaseModel):
    league_id: int
    participant_id: int
    team_name: str | None = None


class LeagueParticipantRegister(BaseModel):
    league_id: int
    name: str
    team_name: str


class LeagueParticipantUpdateBiwenger(BaseModel):
    biwenger_user_id: int | None


class LeagueParticipantResponse(BaseModel):
    id: int
    league_id: int
    participant_id: int
    team_name: str | None
    biwenger_user_id: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)