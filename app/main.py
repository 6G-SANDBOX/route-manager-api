# app/main.py
import logging
from fastapi import FastAPI
import asyncio
from app.core.logging import configure_logging
from app.db.database import create_db_and_tables, get_engine
from app.services.routes import load_database_routes_to_system
from app.routers import routes
from app.services.lifecycle import route_manager_loop

configure_logging()
logger = logging.getLogger(__name__)


app = FastAPI()

def configure_app(app: FastAPI) -> None:
    logger.info("Registering FastAPI routers")
    app.include_router(routes.routes)

@app.on_event("startup")
async def on_startup():
    # It is only executed if the database is not in-memory (to avoid tests)
    engine_url = str(get_engine().url)
    if "memory" not in engine_url:
        logger.info("Creating tables for production DB")
        create_db_and_tables()

        logger.info("Loading stored routes")
        load_database_routes_to_system()

        logger.info("Starting route manager loop")
        asyncio.create_task(route_manager_loop())

configure_app(app)
