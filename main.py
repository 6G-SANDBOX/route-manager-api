# app/main.py
import uvicorn
import logging
from app.database import engine, Base
from app.routers import router
from app.scheduler import scheduler
from app.models import RouteModel
from app.utils import run_command
from app.schemas import Route
from datetime import datetime
from app.config import get_variable


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Create DB tables
Base.metadata.create_all(bind=engine)

def load_scheduled_routes():
    from app.database import SessionLocal
    from app.schemas import Route
    from app.models import RouteModel
    from app.routers.routes import add_route, delete_route
    logger.info("Loading scheduled routes from database")
    db = SessionLocal()
    try:
        routes = db.query(RouteModel).all()
        for db_route in routes:
            route = Route(
                destination=db_route.destination,
                gateway=db_route.gateway,
                interface=db_route.interface,
                create_at=db_route.create_at,
                delete_at=db_route.delete_at
            )
            now = datetime.now()
            if route.create_at and route.create_at > now:
                scheduler.add_job(add_route, 'date', run_date=route.create_at, args=[route])
            else:
                add_route(route)

            if route.delete_at and route.delete_at > now:
                scheduler.add_job(delete_route, 'date', run_date=route.delete_at, args=[route])

            logger.info(f"Route loaded and scheduled: {route}")
    except Exception as e:
        logger.error(f"Error loading routes from database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("Starting Route Manager service - loading routes")
    load_scheduled_routes()
    PORT = int(get_variable('PORT'))

    uvicorn.run("app:app", host="0.0.0.0", port=PORT, reload=True)
