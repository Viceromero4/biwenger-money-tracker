from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.league import League
from app.models.league_participant import LeagueParticipant
from app.schemas.balance import ParticipantBalanceResponse
from app.services.balance_service import calculate_participant_balance


router = APIRouter(
    prefix="/balances",
    tags=["balances"],
)


@router.get(
    "/{league_participant_id}",
    response_model=ParticipantBalanceResponse,
)
def get_participant_balance(
    league_participant_id: int,
    db: Session = Depends(get_db),
):
    league_participant = db.get(
        LeagueParticipant,
        league_participant_id,
    )

    if league_participant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League participant not found",
        )

    return calculate_participant_balance(
        db,
        league_participant,
    )


@router.get(
    "/league/{league_id}",
    response_model=list[ParticipantBalanceResponse],
)
def get_league_balances(
    league_id: int,
    db: Session = Depends(get_db),
):
    league = db.get(
        League,
        league_id,
    )

    if league is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found",
        )

    league_participants = db.scalars(
        select(LeagueParticipant).where(
            LeagueParticipant.league_id == league_id
        )
    ).all()

    return [
        calculate_participant_balance(
            db,
            league_participant,
        )
        for league_participant in league_participants
    ]