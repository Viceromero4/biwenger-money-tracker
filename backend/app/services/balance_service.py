from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.league import League
from app.models.league_participant import LeagueParticipant
from app.models.movement import Movement
from app.models.participant import Participant
from app.schemas.balance import ParticipantBalanceResponse


def calculate_participant_balance(
    db: Session,
    league_participant: LeagueParticipant,
) -> ParticipantBalanceResponse:
    league = db.get(
        League,
        league_participant.league_id,
    )

    participant = db.get(
        Participant,
        league_participant.participant_id,
    )

    movements_total = db.scalar(
        select(
            func.coalesce(
                func.sum(Movement.amount),
                0,
            )
        ).where(
            Movement.league_participant_id == league_participant.id
        )
    )

    current_balance = league.initial_balance + movements_total

    return ParticipantBalanceResponse(
        league_participant_id=league_participant.id,
        participant_id=participant.id,
        participant_name=participant.name,
        league_id=league.id,
        league_name=league.name,
        initial_balance=league.initial_balance,
        movements_total=movements_total,
        current_balance=current_balance,
    )