from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LeagueParticipantCreate(BaseModel):
    league_id: int
    participant_id: int


class LeagueParticipantResponse(BaseModel):
    id: int
    league_id: int
    participant_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)