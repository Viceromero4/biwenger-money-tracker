from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.league import League
from app.schemas.dashboard import LeagueDashboardResponse
from app.services.dashboard_service import build_league_dashboard


router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
)


@router.get(
    "/league/{league_id}",
    response_model=LeagueDashboardResponse,
)
def get_league_dashboard(
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

    return build_league_dashboard(
        db,
        league,
    )