from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.leagues import router as leagues_router
from app.db.session import engine
from app.api.seasons import router as seasons_router
from app.api.participants import router as participants_router
from app.api.league_participants import router as league_participants_router
from app.api.movements import router as movements_router
from app.api.balances import router as balances_router
from app.api.transfers import router as transfers_router
from app.api.dashboard import router as dashboard_router


app = FastAPI(
    title="Biwenger Money Tracker API",
    version="0.1.0",
)

app.include_router(leagues_router)
app.include_router(seasons_router)
app.include_router(participants_router)
app.include_router(league_participants_router)
app.include_router(movements_router)
app.include_router(balances_router)
app.include_router(transfers_router)
app.include_router(dashboard_router)
@app.get("/")
def root():
    return {
        "message": "Biwenger Money Tracker API",
        "status": "running",
    }


@app.get("/health")
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "ok",
            "database": "connected",
        }

    except SQLAlchemyError:
        return {
            "status": "error",
            "database": "disconnected",
        }