from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.league import League
from app.models.league_participant import LeagueParticipant
from app.models.participant import Participant
from app.schemas.league_participant import (
    LeagueParticipantCreate,
    LeagueParticipantResponse,
)
from app.schemas.league_participant import (
    LeagueParticipantCreate,
    LeagueParticipantRegister,
    LeagueParticipantResponse,
)


router = APIRouter(
    prefix="/league-participants",
    tags=["league participants"],
)


@router.post(
    "",
    response_model=LeagueParticipantResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_league_participant(
    data: LeagueParticipantCreate,
    db: Session = Depends(get_db),
):
    league = db.get(League, data.league_id)

    if league is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found",
        )

    participant = db.get(Participant, data.participant_id)

    if participant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found",
        )

    existing = db.scalar(
        select(LeagueParticipant).where(
            LeagueParticipant.league_id == data.league_id,
            LeagueParticipant.participant_id == data.participant_id,
        )
    )

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Participant already belongs to this league",
        )

    league_participant = LeagueParticipant(
        league_id=data.league_id,
        participant_id=data.participant_id,
        team_name=data.team_name,
    )

    db.add(league_participant)
    db.commit()
    db.refresh(league_participant)

    return league_participant

@router.post(
    "/register",
    response_model=LeagueParticipantResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_league_participant(
    data: LeagueParticipantRegister,
    db: Session = Depends(get_db),
):
    league = db.get(League, data.league_id)

    if league is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found",
        )

    participant = db.scalar(
        select(Participant).where(
            Participant.name == data.name
        )
    )

    if participant is None:
        participant = Participant(
            name=data.name,
        )

        db.add(participant)
        db.flush()

    existing = db.scalar(
        select(LeagueParticipant).where(
            LeagueParticipant.league_id == data.league_id,
            LeagueParticipant.participant_id == participant.id,
        )
    )

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Participant already belongs to this league",
        )

    league_participant = LeagueParticipant(
        league_id=data.league_id,
        participant_id=participant.id,
        team_name=data.team_name,
    )

    db.add(league_participant)
    db.commit()
    db.refresh(league_participant)

    return league_participant

@router.get(
    "",
    response_model=list[LeagueParticipantResponse],
)
def get_league_participants(
    db: Session = Depends(get_db),
):
    return db.scalars(select(LeagueParticipant)).all()