# app/main.py
import logging
from fastapi import FastAPI
import asyncio
from app.core.logging import configure_logging
from app.db.database import create_db_and_tables
from app.services.routes import load_database_routes_to_system
from app.routers import routes
from app.services.lifecycle import route_manager_loop

configure_logging()
logger = logging.getLogger(__name__)


app = FastAPI()

def configure_app(app: FastAPI) -> None:
    """
    Configure FastAPI application
    """
    logger.info("Initialize database")
    create_db_and_tables()

    logger.info("Load stored routes")
    load_database_routes_to_system()

    logger.info("Register FastAPI routers")
    app.include_router(routes.routes)

@app.on_event("startup")
async def start_background_tasks():
    asyncio.create_task(route_manager_loop())

configure_app(app)
