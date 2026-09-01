import json
from datetime import datetime, timezone

from app.db.session import SessionLocal
from app.integrations.biwenger.client import BiwengerClient
from app.models.league import League


db = SessionLocal()

try:
    league = db.get(League, 1)

    client = BiwengerClient(
        league_id=league.biwenger_league_id,
    )

    offset = 0
    limit = 8
    found_events = []

    while True:
        board_data = client.get_board(
            offset=offset,
            limit=limit,
        )

        events = board_data["data"]

        if not events:
            break

        for event in events:
            if event["type"] == "loanReturn":
                found_events.append(event)

        if len(events) < limit:
            break

        offset += limit

    print("=" * 60)
    print("LOAN RETURNS DE PURIBET")
    print("=" * 60)

    for event in found_events:
        event_date = datetime.fromtimestamp(
            event["date"],
            tz=timezone.utc,
        )

        print()
        print("FECHA:", event_date)
        print(json.dumps(event, indent=2, ensure_ascii=False))
        print("-" * 60)

finally:
    db.close()