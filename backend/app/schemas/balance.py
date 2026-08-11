from pydantic import BaseModel


class ParticipantBalanceResponse(BaseModel):
    league_participant_id: int
    participant_id: int
    participant_name: str
    league_id: int
    league_name: str
    initial_balance: int
    movements_total: int
    current_balance: int