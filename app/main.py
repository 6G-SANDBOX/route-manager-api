# app/main.py
import logging
from app.core.logging import configure_logging
from fastapi import FastAPI
from app.db.database import create_db_and_tables
# from app.services.routes import load_stored_routes
from app.routers import routes

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
    # load_stored_routes()

    logger.info("Register FastAPI routers")
    app.include_router(routes.routes)

configure_app(app)
