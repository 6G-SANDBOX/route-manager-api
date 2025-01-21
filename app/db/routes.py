# app/db/routes.py
from app.schemas.routes import Route
from app.db.database import SessionLocal, Route as RouteModel
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


def add_route_to_database(route: Route) -> None:
    """
    Adds a route to the database.

    Args:
        route (Route): A Route object containing destination, gateway, interface, create_at, and delete_at.

    Raises:
        Exception: If an error occurs while interacting with the database.
    """
    logger.info(f"Adding route to database: {route}")
    db: Session = SessionLocal()
    try:
        db_route = RouteModel(
            destination=route.destination,
            gateway=route.gateway,
            interface=route.interface,
            create_at=route.create_at or datetime.now(datetime.timezone.utc)(),
            delete_at=route.delete_at
        )
        db.add(db_route)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while adding route: {str(e)}")
        raise Exception(f"Database error: {str(e)}") from e
    finally:
        db.close()

    logger.info("Route {route.destination} added to database successfully")


def delete_route_from_database(route: Route) -> None:
    """
    Deletes a route from the database.

    Args:
        route (Route): A Route object containing destination, gateway, interface, create_at, and delete_at.

    Raises:
        Exception: If an error occurs while interacting with the database.
    """
    logger.info(f"Deleting route from database: {route}")
    db: Session = SessionLocal()
    try:
        db_route = db.query(RouteModel).filter(RouteModel.destination == route.destination).first()
        if db_route:
            db.delete(db_route)
            # db_route.delete_at = datetime.utcnow()    # TODO: Interesante saber que se puede hacer esto, investigar
            db.commit()
            logger.info("Route {route.destination} removed from database successfully")
        else:
            logger.warning("Route {route.destination} not found in database")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while deleting route: {str(e)}")
        raise Exception(f"Database error: {str(e)}") from e
    finally:
        db.close()
