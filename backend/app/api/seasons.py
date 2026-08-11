from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.season import Season
from app.schemas.season import SeasonCreate, SeasonResponse


router = APIRouter(
    prefix="/seasons",
    tags=["seasons"],
)


@router.post(
    "",
    response_model=SeasonResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_season(
    season_data: SeasonCreate,
    db: Session = Depends(get_db),
):
    season = Season(
        name=season_data.name,
    )

    db.add(season)
    db.commit()
    db.refresh(season)

    return season


@router.get(
    "",
    response_model=list[SeasonResponse],
)
def get_seasons(
    db: Session = Depends(get_db),
):
    seasons = db.query(Season).all()

    return seasons