import hashlib
import re


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

def generate_round_bonus_external_key(
    *,
    league_biwenger_id: int,
    round_number: int,
    participant_biwenger_id: int,
) -> str:
    raw_key = (
        f"{league_biwenger_id}|"
        f"round_bonus|"
        f"{round_number}|"
        f"{participant_biwenger_id}"
    )

    return hashlib.sha256(
        raw_key.encode("utf-8")
    ).hexdigest()

def parse_board_events(events, league_biwenger_id: int):
    parsed_movements = []

    for event in events:
        if event["type"] not in [
            "transfer",
            "market",
            "bonus",
            "clauseIncrement",
            "loan",
            "loanReturn",
            "roundFinished",
        ]:
            continue

                # PAGO DE JORNADA
        if event["type"] == "roundFinished":
            content = event["content"]
            round_data = content["round"]

            round_name = round_data["name"]

            match = re.search(r"(?:Jornada|Round)\s+(\d+)", round_name,re.IGNORECASE,)

            if match is None:
                continue

            round_number = int(match.group(1))

            for result in content.get("results", []):
                # Hay eventos roundFinished que todavía no tienen
                # pago económico.
                if "bonus" not in result:
                    continue

                participant = result["user"]

                external_key = generate_round_bonus_external_key(
                    league_biwenger_id=league_biwenger_id,
                    round_number=round_number,
                    participant_biwenger_id=participant["id"],
                )

                reason = result.get("reason", {})

                parsed_movements.append(
                    {
                        "movement_type": "round_bonus",
                        "operation_type": None,
                        "participant_biwenger_id": participant["id"],
                        "participant_name": participant["name"],
                        "player_biwenger_id": None,
                        "amount": result["bonus"],
                        "date": event["date"],
                        "external_key": external_key,
                        "round_number": round_number,
                        "round_name": round_name,
                        "points": result.get("points"),
                        "bonus_point": reason.get("bonusPoint"),
                        "bonus_fixed": reason.get("bonusFixed"),
                        "step": content.get("step"),
                    }
                )

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

            # AUMENTO DE CLÁUSULA
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

            # CESIÓN ENTRE PARTICIPANTES
            elif event["type"] == "loan":
                lender = movement["from"]
                borrower = movement["to"]

                lender_external_key = generate_external_key(
                    league_biwenger_id=league_biwenger_id,
                    event_type=event["type"],
                    date=event["date"],
                    player_biwenger_id=movement["player"],
                    participant_biwenger_id=lender["id"],
                    amount=-movement["amount"],
                    role="lender",
                )

                borrower_external_key = generate_external_key(
                    league_biwenger_id=league_biwenger_id,
                    event_type=event["type"],
                    date=event["date"],
                    player_biwenger_id=movement["player"],
                    participant_biwenger_id=borrower["id"],
                    amount=movement["amount"],
                    role="borrower",
                )

                parsed_movements.append(
                    {
                        "movement_type": "participant_operation",
                        "operation_type": "loan",
                        "from_biwenger_id": lender["id"],
                        "from_name": lender["name"],
                        "to_biwenger_id": borrower["id"],
                        "to_name": borrower["name"],
                        "player_biwenger_id": movement["player"],
                        "amount": movement["amount"],
                        "rounds": movement.get("rounds"),
                        "date": event["date"],
                        "seller_external_key": lender_external_key,
                        "buyer_external_key": borrower_external_key,
                    }
                )
                        # DEVOLUCIÓN DE CESIÓN
            elif event["type"] == "loanReturn":
                from_participant = movement["from"]
                to_participant = movement["to"]
                refund = movement["refund"]

                from_external_key = generate_external_key(
                    league_biwenger_id=league_biwenger_id,
                    event_type=event["type"],
                    date=event["date"],
                    player_biwenger_id=movement["player"],
                    participant_biwenger_id=from_participant["id"],
                    amount=refund,
                    role="from",
                )

                to_external_key = generate_external_key(
                    league_biwenger_id=league_biwenger_id,
                    event_type=event["type"],
                    date=event["date"],
                    player_biwenger_id=movement["player"],
                    participant_biwenger_id=to_participant["id"],
                    amount=-refund,
                    role="to",
                )

                parsed_movements.append(
                    {
                        "movement_type": "participant_operation",
                        "operation_type": "loan_return",
                        "from_biwenger_id": from_participant["id"],
                        "from_name": from_participant["name"],
                        "to_biwenger_id": to_participant["id"],
                        "to_name": to_participant["name"],
                        "player_biwenger_id": movement["player"],
                        "amount": refund,
                        "rounds": movement.get("rounds"),
                        "date": event["date"],
                        "seller_external_key": from_external_key,
                        "buyer_external_key": to_external_key,
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