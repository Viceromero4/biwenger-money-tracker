from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.league import League
from app.models.league_participant import LeagueParticipant
from app.models.participant import Participant
from app.models.season import Season
from app.schemas.dashboard import (
    DashboardParticipant,
    LeagueDashboardResponse,
)
from app.services.balance_service import calculate_participant_balance


def build_league_dashboard(
    db: Session,
    league: League,
) -> LeagueDashboardResponse:
    season = db.get(
        Season,
        league.season_id,
    )

    league_participants = db.scalars(
        select(LeagueParticipant).where(
            LeagueParticipant.league_id == league.id
        )
    ).all()

    participants = []

    for league_participant in league_participants:
        participant = db.get(
            Participant,
            league_participant.participant_id,
        )

        balance = calculate_participant_balance(
            db,
            league_participant,
        )

        participants.append(
            DashboardParticipant(
                league_participant_id=league_participant.id,
                participant_id=participant.id,
                name=participant.name,
                current_balance=balance.current_balance,
            )
        )

    return LeagueDashboardResponse(
        league_id=league.id,
        league_name=league.name,
        season_id=season.id,
        season_name=season.name,
        initial_balance=league.initial_balance,
        participants=participants,
    )