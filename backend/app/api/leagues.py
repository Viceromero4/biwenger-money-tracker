from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.league import League
from app.models.season import Season
from app.schemas.league import (
    LeagueCreate,
    LeagueResponse,
    LeagueUpdateBiwenger,
)


router = APIRouter(
    prefix="/leagues",
    tags=["leagues"],
)


@router.post(
    "",
    response_model=LeagueResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_league(
    league_data: LeagueCreate,
    db: Session = Depends(get_db),
):
    season = db.get(Season, league_data.season_id)

    if season is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Season not found",
        )

    league = League(
        season_id=league_data.season_id,
        name=league_data.name,
        initial_balance=league_data.initial_balance,
    )

    db.add(league)
    db.commit()
    db.refresh(league)

    return league


@router.get(
    "",
    response_model=list[LeagueResponse],
)
def get_leagues(
    db: Session = Depends(get_db),
):
    leagues = db.query(League).all()

    return leagues

@router.patch(
    "/{league_id}/biwenger",
    response_model=LeagueResponse,
)
def update_biwenger_league_id(
    league_id: int,
    league_data: LeagueUpdateBiwenger,
    db: Session = Depends(get_db),
):
    league = db.get(League, league_id)

    if league is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found",
        )

    league.biwenger_league_id = league_data.biwenger_league_id

    db.commit()
    db.refresh(league)

    return league