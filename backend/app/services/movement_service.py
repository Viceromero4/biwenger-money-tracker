from sqlalchemy.orm import Session

from app.models.league_participant import LeagueParticipant
from app.models.movement import Movement, MovementType


from sqlalchemy.orm import Session

from app.models.league_participant import LeagueParticipant
from app.models.movement import Movement, MovementType


def create_movement(
    db: Session,
    *,
    league_participant: LeagueParticipant,
    movement_type: MovementType,
    amount: int,
    player_name: str | None,
    description: str | None,
    occurred_at,
) -> Movement:
    movement = Movement(
        league_participant_id=league_participant.id,
        type=movement_type,
        amount=amount,
        player_name=player_name,
        description=description,
        occurred_at=occurred_at,
    )

    db.add(movement)

    return movement

def create_player_transfer(
    db: Session,
    *,
    buyer: LeagueParticipant,
    seller: LeagueParticipant,
    amount: int,
    player_name: str,
    description: str | None,
    occurred_at,
) -> tuple[Movement, Movement]:
    buyer_movement = create_movement(
        db,
        league_participant=buyer,
        movement_type=MovementType.PURCHASE,
        amount=-amount,
        player_name=player_name,
        description=description,
        occurred_at=occurred_at,
    )

    seller_movement = create_movement(
        db,
        league_participant=seller,
        movement_type=MovementType.SALE,
        amount=amount,
        player_name=player_name,
        description=description,
        occurred_at=occurred_at,
    )

    return buyer_movement, seller_movement

def create_bonus(
    db: Session,
    *,
    league_participant: LeagueParticipant,
    amount: int,
    description: str | None,
    occurred_at,
) -> Movement:
    return create_movement(
        db,
        league_participant=league_participant,
        movement_type=MovementType.BONUS,
        amount=amount,
        player_name=None,
        description=description,
        occurred_at=occurred_at,
    )


def create_market_sale(
    db: Session,
    *,
    league_participant: LeagueParticipant,
    amount: int,
    player_name: str,
    description: str | None,
    occurred_at,
) -> Movement:
    return create_movement(
        db,
        league_participant=league_participant,
        movement_type=MovementType.SALE,
        amount=amount,
        player_name=player_name,
        description=description,
        occurred_at=occurred_at,
    )


def create_clause_compensation(
    db: Session,
    *,
    league_participant: LeagueParticipant,
    amount: int,
    player_name: str,
    description: str | None,
    occurred_at,
) -> Movement:
    return create_movement(
        db,
        league_participant=league_participant,
        movement_type=MovementType.CLAUSE_COMPENSATION,
        amount=amount,
        player_name=player_name,
        description=description,
        occurred_at=occurred_at,
    )


def create_adjustment(
    db: Session,
    *,
    league_participant: LeagueParticipant,
    amount: int,
    description: str,
    occurred_at,
) -> Movement:
    return create_movement(
        db,
        league_participant=league_participant,
        movement_type=MovementType.ADJUSTMENT,
        amount=amount,
        player_name=None,
        description=description,
        occurred_at=occurred_at,
    )