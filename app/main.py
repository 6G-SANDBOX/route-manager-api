# app/main.py
import logging
import uvicorn
from fastapi import FastAPI
from app.routers import routes
from app.db.database import Base, engine
from app.core.config import settings
from app.core.logging import configure_logging
from app.services.routes import load_stored_routes



# Configure logging
configure_logging()
logger = logging.getLogger(__name__)


# Create FastAPI application
app = FastAPI()

def configure_app(app: FastAPI) -> None:
    """
    Configure FastAPI application
    """
    # Create DB tables
    logger.info("Initialize database")
    Base.metadata.create_all(bind=engine)

    # Load stored rules from database
    load_stored_routes()

    # Load application endpoints
    app.include_router(routes.routes)


configure_app(app)
