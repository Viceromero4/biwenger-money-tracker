from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.integrations.biwenger.client import BiwengerClient
from app.integrations.biwenger.parser import parse_board_events
from app.models.league import League
from app.models.league_participant import LeagueParticipant
from app.models.movement import Movement, MovementType
from app.models.participant import Participant
from app.services.movement_service import create_movement


def sync_participants(db: Session, league_id: int):
    league = db.get(League, league_id)

    if league is None:
        raise ValueError("League not found")

    if league.biwenger_league_id is None:
        raise ValueError("League does not have a Biwenger league ID")

    client = BiwengerClient(
        league_id=league.biwenger_league_id,
    )

    data = client.get_league()
    standings = data["data"]["standings"]

    results = []

    for biwenger_participant in standings:
        biwenger_user_id = biwenger_participant["id"]
        name = biwenger_participant["name"]

        existing = db.scalar(
            select(LeagueParticipant).where(
                LeagueParticipant.league_id == league_id,
                LeagueParticipant.biwenger_user_id == biwenger_user_id,
            )
        )

        if existing is not None:
            results.append(
                {
                    "biwenger_user_id": biwenger_user_id,
                    "name": name,
                    "action": "already_exists",
                }
            )
            continue

        participant = Participant(
            name=name,
        )

        db.add(participant)
        db.flush()

        league_participant = LeagueParticipant(
            league_id=league_id,
            participant_id=participant.id,
            team_name=name,
            biwenger_user_id=biwenger_user_id,
        )

        db.add(league_participant)

        results.append(
            {
                "biwenger_user_id": biwenger_user_id,
                "name": name,
                "action": "created",
            }
        )

    db.commit()

    return results


def sync_movements(db: Session, league_id: int):
    league = db.get(League, league_id)

    if league is None:
        raise ValueError("League not found")

    if league.biwenger_league_id is None:
        raise ValueError("League does not have a Biwenger league ID")

    if league.sync_from is None:
        raise ValueError("League does not have a sync_from date")

    client = BiwengerClient(
        league_id=league.biwenger_league_id,
    )

    # ---------------------------------------------------------
    # 1. RECORRER EL BOARD HASTA LA FECHA DE INICIO DE LA LIGA
    # ---------------------------------------------------------

    offset = 0
    limit = 8
    board_events = []
    reached_sync_from = False

    while not reached_sync_from:
        board_data = client.get_board(
            offset=offset,
            limit=limit,
        )

        events = board_data["data"]

        if not events:
            break

        for event in events:
            event_date = datetime.fromtimestamp(
                event["date"],
                tz=timezone.utc,
            )

            if event_date < league.sync_from:
                reached_sync_from = True
                break

            board_events.append(event)

        if reached_sync_from:
            break

        if len(events) < limit:
            break

        offset += limit

    # ---------------------------------------------------------
    # 2. OBTENER CATÁLOGO DE JUGADORES
    # ---------------------------------------------------------

    competition_data = client.get_competition_data(
        competition="la-liga",
        score_id=2,
    )

    players = competition_data["data"]["players"]

    # ---------------------------------------------------------
    # 3. INTERPRETAR EVENTOS ECONÓMICOS
    # ---------------------------------------------------------

    parsed_movements = parse_board_events(
        board_events,
        league_biwenger_id=league.biwenger_league_id,
    )

    results = []

    # ---------------------------------------------------------
    # 4. CREAR MOVIMIENTOS SIN DUPLICADOS
    # ---------------------------------------------------------

    for parsed in parsed_movements:
        # Los clausulazos se procesarán aparte.
        if parsed["movement_type"] == "participant_operation":
            continue

        external_key = parsed["external_key"]

        existing_movement = db.scalar(
            select(Movement).where(
                Movement.external_key == external_key,
            )
        )

        if existing_movement is not None:
            results.append(
                {
                    "external_key": external_key,
                    "action": "already_exists",
                }
            )
            continue

        league_participant = db.scalar(
            select(LeagueParticipant).where(
                LeagueParticipant.league_id == league_id,
                LeagueParticipant.biwenger_user_id
                == parsed["participant_biwenger_id"],
            )
        )

        if league_participant is None:
            results.append(
                {
                    "external_key": external_key,
                    "action": "participant_not_found",
                    "participant_biwenger_id": parsed[
                        "participant_biwenger_id"
                    ],
                }
            )
            continue

        # -----------------------------------------------------
        # RESOLVER NOMBRE DEL FUTBOLISTA
        # -----------------------------------------------------

        player_name = None

        player_biwenger_id = parsed["player_biwenger_id"]

        if player_biwenger_id is not None:
            player = players.get(
                str(player_biwenger_id)
            )

            if player is not None:
                player_name = player["name"]

        occurred_at = datetime.fromtimestamp(
            parsed["date"],
            tz=timezone.utc,
        )

        create_movement(
            db,
            league_participant=league_participant,
            movement_type=MovementType(parsed["movement_type"]),
            amount=parsed["amount"],
            player_name=player_name,
            description="Imported from Biwenger",
            occurred_at=occurred_at,
            external_key=external_key,
        )

        results.append(
            {
                "external_key": external_key,
                "action": "created",
                "player_name": player_name,
            }
        )

    db.commit()

    return results