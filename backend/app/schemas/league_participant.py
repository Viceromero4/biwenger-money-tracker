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

class LeagueParticipantResponse(BaseModel):
    id: int
    league_id: int
    participant_id: int
    team_name: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)