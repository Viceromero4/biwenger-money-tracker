from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.league_participant import LeagueParticipant
from app.models.movement import Movement
from app.schemas.movement import MovementCreate, MovementResponse
from app.models.league import League
from app.services.movement_service import create_movement

router = APIRouter(
    prefix="/movements",
    tags=["movements"],
)


@router.post(
    "",
    response_model=MovementResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_movement(
    movement_data: MovementCreate,
    db: Session = Depends(get_db),
):
    league_participant = db.get(
        LeagueParticipant,
        movement_data.league_participant_id,
    )

    if league_participant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League participant not found",
        )

    movement = create_movement(
        db,
        league_participant=league_participant,
        movement_type=movement_data.type,
        amount=movement_data.amount,
        player_name=movement_data.player_name,
        description=movement_data.description,
        occurred_at=movement_data.occurred_at,
    )

    db.commit()
    db.refresh(movement)

    return movement


@router.get(
    "",
    response_model=list[MovementResponse],
)
def get_movements(
    db: Session = Depends(get_db),
):
    return db.scalars(
        select(Movement).order_by(Movement.occurred_at.desc())
    ).all()

@router.get(
    "/participant/{league_participant_id}",
    response_model=list[MovementResponse],
)
def get_participant_movements(
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

    return db.scalars(
        select(Movement)
        .where(
            Movement.league_participant_id == league_participant_id
        )
        .order_by(Movement.occurred_at.desc())
    ).all()

@router.get(
    "/league/{league_id}",
    response_model=list[MovementResponse],
)
def get_league_movements(
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

    return db.scalars(
        select(Movement)
        .join(
            LeagueParticipant,
            Movement.league_participant_id == LeagueParticipant.id,
        )
        .where(
            LeagueParticipant.league_id == league_id
        )
        .order_by(Movement.occurred_at.desc())
    ).all()