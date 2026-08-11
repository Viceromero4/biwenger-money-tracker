from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.league_participant import LeagueParticipant
from app.schemas.movement import MovementResponse
from app.schemas.transfer import PlayerTransferCreate
from app.services.movement_service import create_player_transfer


router = APIRouter(
    prefix="/transfers",
    tags=["transfers"],
)


@router.post(
    "",
    response_model=list[MovementResponse],
    status_code=status.HTTP_201_CREATED,
)
def create_transfer(
    transfer_data: PlayerTransferCreate,
    db: Session = Depends(get_db),
):
    buyer = db.get(
        LeagueParticipant,
        transfer_data.buyer_league_participant_id,
    )

    if buyer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Buyer league participant not found",
        )

    seller = db.get(
        LeagueParticipant,
        transfer_data.seller_league_participant_id,
    )

    if seller is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seller league participant not found",
        )

    if buyer.league_id != seller.league_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Buyer and seller must belong to the same league",
        )

    buyer_movement, seller_movement = create_player_transfer(
        db,
        buyer=buyer,
        seller=seller,
        amount=transfer_data.amount,
        player_name=transfer_data.player_name,
        description=transfer_data.description,
        occurred_at=transfer_data.occurred_at,
    )

    db.commit()

    db.refresh(buyer_movement)
    db.refresh(seller_movement)

    return [
        buyer_movement,
        seller_movement,
    ]