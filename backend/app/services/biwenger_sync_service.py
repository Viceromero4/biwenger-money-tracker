from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.integrations.biwenger.client import BiwengerClient
from app.integrations.biwenger.parser import parse_board_events
from app.models.league import League
from app.models.league_participant import LeagueParticipant
from app.models.movement import (
    Movement,
    MovementOperationType,
    MovementType,
)
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

    sync_started_at = datetime.now(timezone.utc)

    client = BiwengerClient(
        league_id=league.biwenger_league_id,
    )

    # ---------------------------------------------------------
    # 1. CALCULAR DESDE QUÉ FECHA SINCRONIZAR
    # ---------------------------------------------------------

    sync_cutoff = league.sync_from

    if league.last_synced_at is not None:
        safety_cutoff = league.last_synced_at - timedelta(days=7)

        if safety_cutoff > sync_cutoff:
            sync_cutoff = safety_cutoff

    # ---------------------------------------------------------
    # 2. RECORRER EL BOARD HASTA LA FECHA DE CORTE
    # ---------------------------------------------------------

    offset = 0
    limit = 8
    board_events = []
    reached_cutoff = False

    while not reached_cutoff:
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

            if event_date < sync_cutoff:
                reached_cutoff = True
                break

            board_events.append(event)

        if reached_cutoff:
            break

        if len(events) < limit:
            break

        offset += limit

    # ---------------------------------------------------------
    # 3. CATÁLOGO DE JUGADORES
    # ---------------------------------------------------------

    competition_data = client.get_competition_data(
        competition="la-liga",
        score_id=2,
    )

    players = competition_data["data"]["players"]

    # ---------------------------------------------------------
    # 4. PARSEAR EVENTOS ECONÓMICOS
    # ---------------------------------------------------------

    parsed_movements = parse_board_events(
        board_events,
        league_biwenger_id=league.biwenger_league_id,
    )
        # ---------------------------------------------------------
    # DEDUPLICAR PAGOS DE JORNADA
    #
    # Una misma jornada puede aparecer varias veces
    # (por ejemplo Round 1 y Round 1 postponed).
    # Nos quedamos con la versión más reciente.
    # ---------------------------------------------------------

    round_bonus_by_key = {}
    other_movements = []

    for parsed in parsed_movements:
        if parsed["movement_type"] != "round_bonus":
            other_movements.append(parsed)
            continue

        external_key = parsed["external_key"]

        existing_parsed = round_bonus_by_key.get(external_key)

        if (
            existing_parsed is None
            or parsed["date"] > existing_parsed["date"]
        ):
            round_bonus_by_key[external_key] = parsed

    parsed_movements = (
        other_movements
        + list(round_bonus_by_key.values())
    )

    results = []

    # ---------------------------------------------------------
    # 5. PROCESAR MOVIMIENTOS
    # ---------------------------------------------------------

    for parsed in parsed_movements:
        player_name = None

        player_biwenger_id = parsed["player_biwenger_id"]

        if player_biwenger_id is not None:
            player = players.get(str(player_biwenger_id))

            if player is not None:
                player_name = player["name"]

        occurred_at = datetime.fromtimestamp(
            parsed["date"],
            tz=timezone.utc,
        )

        # =====================================================
        # OPERACIONES ENTRE PARTICIPANTES
        # =====================================================

        if parsed["movement_type"] == "participant_operation":
            from_participant = db.scalar(
                select(LeagueParticipant).where(
                    LeagueParticipant.league_id == league_id,
                    LeagueParticipant.biwenger_user_id
                    == parsed["from_biwenger_id"],
                )
            )

            to_participant = db.scalar(
                select(LeagueParticipant).where(
                    LeagueParticipant.league_id == league_id,
                    LeagueParticipant.biwenger_user_id
                    == parsed["to_biwenger_id"],
                )
            )

            if from_participant is None or to_participant is None:
                results.append(
                    {
                        "action": "participant_not_found",
                        "operation_type": parsed["operation_type"],
                    }
                )
                continue

            operation_type = MovementOperationType(
                parsed["operation_type"]
            )

            # CLAUSULAZO
            #
            # El jugador sale del vendedor y llega al comprador.
            # Comprador paga.
            # Vendedor cobra.
            if parsed["operation_type"] == "clause":
                from_amount = parsed["amount"]
                to_amount = -parsed["amount"]

                from_type = MovementType.SALE
                to_type = MovementType.PURCHASE

            # CESIÓN
            #
            # FROM = propietario que cede el jugador.
            # TO = participante que recibe al jugador.
            #
            # El receptor paga al propietario.
            if parsed["operation_type"] == "loan":
                from_amount = parsed["amount"]
                to_amount = -parsed["amount"]

                from_type = MovementType.SALE
                to_type = MovementType.PURCHASE

            if parsed["operation_type"] == "loan_return":
                from_amount = parsed["amount"]
                to_amount = -parsed["amount"]

                from_type = MovementType.SALE
                to_type = MovementType.PURCHASE

            if parsed["operation_type"] not in [
                "clause",
                "loan",
                "loan_return",
            ]:
                continue

            from_external_key = parsed["seller_external_key"]
            to_external_key = parsed["buyer_external_key"]
            # -------------------------------------------------
            # MOVIMIENTO FROM
            # -------------------------------------------------

            from_existing = db.scalar(
                select(Movement).where(
                    Movement.external_key == from_external_key,
                )
            )

            if from_existing is None:
                create_movement(
                    db,
                    league_participant=from_participant,
                    movement_type=from_type,
                    operation_type=operation_type,
                    amount=from_amount,
                    player_name=player_name,
                    description="Imported from Biwenger",
                    occurred_at=occurred_at,
                    external_key=from_external_key,
                )

                results.append(
                    {
                        "external_key": from_external_key,
                        "action": "created",
                        "player_name": player_name,
                    }
                )
            else:
                results.append(
                    {
                        "external_key": from_external_key,
                        "action": "already_exists",
                    }
                )

            # -------------------------------------------------
            # MOVIMIENTO TO
            # -------------------------------------------------

            to_existing = db.scalar(
                select(Movement).where(
                    Movement.external_key == to_external_key,
                )
            )

            if to_existing is None:
                create_movement(
                    db,
                    league_participant=to_participant,
                    movement_type=to_type,
                    operation_type=operation_type,
                    amount=to_amount,
                    player_name=player_name,
                    description="Imported from Biwenger",
                    occurred_at=occurred_at,
                    external_key=to_external_key,
                )

                results.append(
                    {
                        "external_key": to_external_key,
                        "action": "created",
                        "player_name": player_name,
                    }
                )
            else:
                results.append(
                    {
                        "external_key": to_external_key,
                        "action": "already_exists",
                    }
                )

            continue

        # =====================================================
        # MOVIMIENTOS DE UN PARTICIPANTE
        # =====================================================

        external_key = parsed["external_key"]

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

        existing_movement = db.scalar(
            select(Movement).where(
                Movement.external_key == external_key,
            )
        )

        # =====================================================
        # PAGO DE JORNADA
        # =====================================================

        if parsed["movement_type"] == "round_bonus":
            if existing_movement is None:
                create_movement(
                    db,
                    league_participant=league_participant,
                    movement_type=MovementType.ROUND_BONUS,
                    amount=parsed["amount"],
                    player_name=None,
                    description=parsed.get("round_name"),
                    occurred_at=occurred_at,
                    external_key=external_key,
                    round_number=parsed["round_number"],
                )

                results.append(
                    {
                        "external_key": external_key,
                        "action": "created",
                        "round_number": parsed["round_number"],
                        "amount": parsed["amount"],
                    }
                )

            # Solo actualizamos si el evento encontrado es
            # posterior al que ya tenemos guardado.
            #
            # Esto es importante porque el board viene
            # ordenado de más nuevo a más antiguo.
            elif occurred_at > existing_movement.occurred_at:
                previous_amount = existing_movement.amount

                existing_movement.amount = parsed["amount"]
                existing_movement.round_number = parsed["round_number"]
                existing_movement.description = parsed.get("round_name")
                existing_movement.occurred_at = occurred_at

                results.append(
                    {
                        "external_key": external_key,
                        "action": "updated",
                        "round_number": parsed["round_number"],
                        "previous_amount": previous_amount,
                        "amount": parsed["amount"],
                    }
                )

            else:
                results.append(
                    {
                        "external_key": external_key,
                        "action": "already_exists",
                    }
                )

            continue

        # =====================================================
        # RESTO DE MOVIMIENTOS
        # =====================================================

        if existing_movement is not None:
            results.append(
                {
                    "external_key": external_key,
                    "action": "already_exists",
                }
            )
            continue

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

    # ---------------------------------------------------------
    # 6. GUARDAR ÚLTIMA SINCRONIZACIÓN
    # ---------------------------------------------------------

    league.last_synced_at = sync_started_at

    db.commit()

    return results