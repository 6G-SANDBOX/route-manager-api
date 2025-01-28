# app/services/routes.py
import logging
import json
import subprocess
from datetime import datetime, timezone
from fastapi import HTTPException
from pydantic import ValidationError
from app.db.routes import get_routes_from_database
from app.services.utils  import run_command
from app.schemas.routes import Route

logger = logging.getLogger(__name__)


def load_database_routes_to_system() -> None:
    """
    Load active routes from the database and applies them to the system.
    """
    logger.info("LOAD ACTIVE ROUTES FROM THE DATABASE TO THE SYSTEM")
    try:
        database_routes: list[dict] = get_routes_from_database()
    except:
        raise HTTPException(status_code=500, detail="Error fetching routes from database")

    for route in database_routes:

        # TODO: function that checks if a route EXPIRED and deletes it
        # TODO: function that checks if a route BEGAN and modifies active from it

        if route["active"]:
            try:
                add_route_to_system(Route(**route))

            except (ValidationError, ValueError, TypeError) as e:
                logger.error(f"Error impoting route from database: {route}")
                logger.error(f"Error details: {e}")
            except subprocess.CalledProcessError as e:
                if "RTNETLINK answers: File exists" in e.stderr.strip():
                    logger.warning(f"Route from database to {route["to"]} already existed in the system")
                    return
                raise HTTPException(status_code=500, detail=f"{e.stderr.strip()}")


def add_route_to_system(route: Route) -> bool:
    """
    Adds a route to the system using the `ip route add` command.

    Args:
        route (Route): A Route object containing to, via, dev, create_at, and delete_at.

    Returns:
        bool: True if the route was added successfully, False otherwise.
    """
    logger.info("Adding route to system...")
    command: list[str] = ["ip", "route", "add", "to", str(route.to)]
    command.extend(["via", str(route.via)]) if route.via else command
    command.extend(["dev", route.dev]) if route.dev else command

    try:
        run_command(command) 
    except subprocess.CalledProcessError:
        raise
    
    logger.info(f"Route to {route.to} added to system successfully")
    return True


def delete_route_from_system(to: str) -> bool:
    """
    Deletes a route from the system using the `ip` command.

    Args:
        to (str): The destination IP Address/Network of the route to delete.

    Returns:
        bool: True if the route was deleted successfully, False otherwise.
    """
    logger.info("Deleting route from system...")
    try:
        run_command(["ip", "route", "del", "to", to])
    except subprocess.CalledProcessError:
        raise
    
    logger.info(f"Route to {to} deleted from system successfully")
    return True
