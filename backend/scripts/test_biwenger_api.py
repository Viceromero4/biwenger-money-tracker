from app.db.session import SessionLocal
from app.services.biwenger_sync_service import sync_movements


db = SessionLocal()

try:
    results = sync_movements(
        db=db,
        league_id=1,
    )

    created = 0
    updated = 0
    already_exists = 0
    participant_not_found = 0

    for result in results:
        print(result)

        if result["action"] == "created":
            created += 1

        elif result["action"] == "updated":
            updated += 1

        elif result["action"] == "already_exists":
            already_exists += 1

        elif result["action"] == "participant_not_found":
            participant_not_found += 1

    print()
    print("=" * 60)
    print("RESUMEN")
    print("=" * 60)
    print("Creados:", created)
    print("Actualizados:", updated)
    print("Ya existentes:", already_exists)
    print("Participante no encontrado:", participant_not_found)

finally:
    db.close()