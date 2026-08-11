from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.participant import Participant
from app.schemas.participant import ParticipantCreate, ParticipantResponse


router = APIRouter(
    prefix="/participants",
    tags=["participants"],
)


@router.post(
    "",
    response_model=ParticipantResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_participant(
    participant_data: ParticipantCreate,
    db: Session = Depends(get_db),
):
    participant = Participant(
        name=participant_data.name,
    )

    db.add(participant)
    db.commit()
    db.refresh(participant)

    return participant


@router.get(
    "",
    response_model=list[ParticipantResponse],
)
def get_participants(
    db: Session = Depends(get_db),
):
    participants = db.query(Participant).all()

    return participants