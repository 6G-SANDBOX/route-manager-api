# app/main.py
from app.core.logging import configure_logging
import logging
from fastapi import FastAPI
from app.db.database import Base, engine
from app.services.routes import load_stored_routes
from app.routers import routes

configure_logging()
logger = logging.getLogger(__name__)


app = FastAPI()

def configure_app(app: FastAPI) -> None:
    """
    Configure FastAPI application
    """
    logger.info("Initialize database")
    Base.metadata.create_all(bind=engine)

    logger.info("Load stored routes")
    load_stored_routes()

    logger.info("Register FastAPI routers")
    app.include_router(routes.routes)
configure_app(app)
