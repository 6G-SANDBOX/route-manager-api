# app/services/routes.py
import logging
from typing import Dict, List, Union
from fastapi import HTTPException
from datetime import datetime, UTC
from sqlalchemy.orm import Session
from app.services.utils import validate_route, run_command, route_exists
from app.schemas.routes import Route
from app.db.database import SessionLocal
from app.core.scheduler import add_job
from app.db.models.routes import RouteModel


logger = logging.getLogger(__name__)


def load_stored_routes() -> None:
    """
    Load active routes from the database to the system.
    """
    logger.info("Loading active routes from database")
    db: Session = SessionLocal()
    try:
        now = datetime.now()
        stored_routes = db.query(RouteModel).all()

        for db_route in stored_routes:
            try:
                route = Route.model_validate(db_route)

                if route.delete_at and route.delete_at < now:
                    delete_route(route)
                    break
                else:
                    schedule_add_route(route)

            except Exception as e:
                logger.error(f"Error processing route {db_route}: {e}")

    except Exception as e:
        logger.error(f"Error loading routes from database: {e}")
    finally:
        db.close()


def get_active_routes() -> Dict[str, List[str]]:
    """
    Fetches all active routes.

    Returns:
        Dict[str, List[str]]: A Diccionary with key word "routes" and a list of active routes as value
    """
    command: str = "ip route show"
    output: str = run_command(command)
    return {"routes": [s.strip() for s in output.splitlines()]}


def schedule_add_route(route: Route) -> Union[None, HTTPException]:
    """
    Schedules a new route to be added, with optional creation and deletion times.

    Args:
        route (Route): The route to schedule

    Returns:
        HTTPException: If the route already exists or if there is an error during scheduling.
    """
    validate_route(route)
    now = datetime.now(UTC) if route.create_at and route.create_at.tzinfo else datetime.now()

    if route.delete_at and route.delete_at <= now:
        raise HTTPException(status_code=409, detail="Route delete_at timestamp has already passed")
    elif route_exists(route.destination, route.gateway, route.interface):
        raise HTTPException(status_code=409, detail="Route already exists")

    logger.info(f"Scheduling addition of route: {route}")

    if route.create_at and (route.create_at > now):
        logger.info(f"Scheduling addition of route {route} at {route.create_at}")
        add_job(add_route, 'date', run_date=route.create_at, args=[route])
    else:
        add_route(route)

    if route.delete_at:
        logger.info(f"Scheduling deletion of route {route} at {route.delete_at}")
        add_job(delete_route, 'date', run_date=route.delete_at, args=[route])


def add_route(route: Route) -> None:
    """
    Adds a new route to route-manager.

    Args:
        route (Route): The route details to be added.
    """
    db = SessionLocal()
    try:
        logger.info(f"Adding route: {route}")

        # Add route to system with iproute2
        command = f"ip route add {route.destination}"
        if route.gateway:
            command += f" via {route.gateway}"
        if route.interface:
            command += f" dev {route.interface}"
        run_command(command)

        # Add route to database with SQLite
        # TODO: Rethink ID. Should format timestamps before adding them
        db_route = RouteModel(
            id=f"{route.destination}_{route.gateway}_{route.interface}",
            destination=route.destination,
            gateway=route.gateway,
            interface=route.interface,
            create_at=route.create_at,
            delete_at=route.delete_at,
        )
        db.add(db_route)
        db.commit()
        db.refresh(db_route)

        logger.info("Route added successfully")

    except Exception as e:
        logger.error(f"Error adding route: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to add route")

    finally:
        db.close()
    

def delete_route(route: Route) -> None:
    """
    Deletes a route to route-manager.

    Args:
        route (Route): The route details to be deleted.
    """
    validate_route(route)
    db = SessionLocal()

    try:
        if not route_exists (route.destination, route.gateway, route.interface):
            raise HTTPException(status_code=409, detail="Route does not exist")

        logger.info(f"Deleting route: {route}")

        # Deleting route to system with iproute2
        command = f"ip route del {route.destination}"
        if route.gateway:
            command += f" via {route.gateway}"
        if route.interface:
            command += f" dev {route.interface}"
        run_command(command)

        # Remove route from database with SQLite
        # TODO: Rethink ID. Should format timestamps before adding them
        db_route = db.query(RouteModel).filter(
            RouteModel.destination == route.destination,
            RouteModel.gateway == route.gateway,
            RouteModel.interface == route.interface
        ).first()
        if db_route:
            db.delete(db_route)
            db.commit()
        else:
            logger.warning(f"Route not found in database: {route}")

        logger.info("Route removed successfully")

    except Exception as e:
        logger.error(f"Error removing route: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to remove route")

    finally:
        db.close()
