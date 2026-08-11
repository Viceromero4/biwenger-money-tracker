from pydantic import BaseModel


class DashboardParticipant(BaseModel):
    league_participant_id: int
    participant_id: int
    name: str
    current_balance: int


class LeagueDashboardResponse(BaseModel):
    league_id: int
    league_name: str
    season_id: int
    season_name: str
    initial_balance: int
    participants: list[DashboardParticipant]