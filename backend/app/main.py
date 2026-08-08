from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import engine


app = FastAPI(
    title="Biwenger Money Tracker API",
    version="0.1.0",
)


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