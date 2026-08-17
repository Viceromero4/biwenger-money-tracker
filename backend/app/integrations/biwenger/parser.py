import hashlib


def generate_external_key(
    *,
    league_biwenger_id: int,
    event_type: str,
    date: int,
    player_biwenger_id: int | None,
    participant_biwenger_id: int | None,
    amount: int,
    role: str | None = None,
) -> str:
    raw_key = (
        f"{league_biwenger_id}|"
        f"{event_type}|"
        f"{date}|"
        f"{player_biwenger_id}|"
        f"{participant_biwenger_id}|"
        f"{amount}|"
        f"{role}"
    )

    return hashlib.sha256(
        raw_key.encode("utf-8")
    ).hexdigest()


def parse_board_events(events, league_biwenger_id: int):
    parsed_movements = []

    for event in events:
        if event["type"] not in ["transfer", "market", "bonus", "clauseIncrement",]:
            continue

        for movement in event["content"]:

            # COMPRA AL MERCADO
            if event["type"] == "market":
                participant = movement["to"]

                external_key = generate_external_key(
                    league_biwenger_id=league_biwenger_id,
                    event_type=event["type"],
                    date=event["date"],
                    player_biwenger_id=movement["player"],
                    participant_biwenger_id=participant["id"],
                    amount=-movement["amount"],
                )

                parsed_movements.append(
                    {
                        "movement_type": "purchase",
                        "operation_type": None,
                        "participant_biwenger_id": participant["id"],
                        "participant_name": participant["name"],
                        "player_biwenger_id": movement["player"],
                        "amount": -movement["amount"],
                        "date": event["date"],
                        "external_key": external_key,
                    }
                )

            # BONUS / PENALIZACIÓN
            elif event["type"] == "bonus":
                participant = movement["user"]

                external_key = generate_external_key(
                    league_biwenger_id=league_biwenger_id,
                    event_type=event["type"],
                    date=event["date"],
                    player_biwenger_id=None,
                    participant_biwenger_id=participant["id"],
                    amount=movement["amount"],
                )

                parsed_movements.append(
                    {
                        "movement_type": "bonus",
                        "operation_type": None,
                        "participant_biwenger_id": participant["id"],
                        "participant_name": participant["name"],
                        "player_biwenger_id": None,
                        "amount": movement["amount"],
                        "date": event["date"],
                        "external_key": external_key,
                    }
                )

            elif event["type"] == "clauseIncrement":
                participant = movement["user"]

                external_key = generate_external_key(
                    league_biwenger_id=league_biwenger_id,
                    event_type=event["type"],
                    date=event["date"],
                    player_biwenger_id=movement["player"],
                    participant_biwenger_id=participant["id"],
                    amount=-movement["amount"],
                )

                parsed_movements.append(
                    {
                        "movement_type": "adjustment",
                        "operation_type": None,
                        "participant_biwenger_id": participant["id"],
                        "participant_name": participant["name"],
                        "player_biwenger_id": movement["player"],
                        "amount": -movement["amount"],
                        "date": event["date"],
                        "external_key": external_key,
                    }
                )    

            # TRANSFERENCIAS / VENTAS / CLÁUSULAS
            elif event["type"] == "transfer":

                # CLAUSULAZO
                if movement.get("type") == "clause":
                    seller_external_key = generate_external_key(
                        league_biwenger_id=league_biwenger_id,
                        event_type=event["type"],
                        date=event["date"],
                        player_biwenger_id=movement["player"],
                        participant_biwenger_id=movement["from"]["id"],
                        amount=movement["amount"],
                        role="seller",
                    )

                    buyer_external_key = generate_external_key(
                        league_biwenger_id=league_biwenger_id,
                        event_type=event["type"],
                        date=event["date"],
                        player_biwenger_id=movement["player"],
                        participant_biwenger_id=movement["to"]["id"],
                        amount=-movement["amount"],
                        role="buyer",
                    )

                    parsed_movements.append(
                        {
                            "movement_type": "participant_operation",
                            "operation_type": "clause",
                            "from_biwenger_id": movement["from"]["id"],
                            "from_name": movement["from"]["name"],
                            "to_biwenger_id": movement["to"]["id"],
                            "to_name": movement["to"]["name"],
                            "player_biwenger_id": movement["player"],
                            "amount": movement["amount"],
                            "date": event["date"],
                            "seller_external_key": seller_external_key,
                            "buyer_external_key": buyer_external_key,
                        }
                    )

                # VENTA AL MERCADO
                elif "to" not in movement:
                    participant = movement["from"]

                    external_key = generate_external_key(
                        league_biwenger_id=league_biwenger_id,
                        event_type=event["type"],
                        date=event["date"],
                        player_biwenger_id=movement["player"],
                        participant_biwenger_id=participant["id"],
                        amount=movement["amount"],
                    )

                    parsed_movements.append(
                        {
                            "movement_type": "sale",
                            "operation_type": None,
                            "participant_biwenger_id": participant["id"],
                            "participant_name": participant["name"],
                            "player_biwenger_id": movement["player"],
                            "amount": movement["amount"],
                            "date": event["date"],
                            "external_key": external_key,
                        }
                    )

    return parsed_movements