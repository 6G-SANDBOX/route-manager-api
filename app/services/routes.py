# app/services/routes.py
import logging
import subprocess
from fastapi import HTTPException
from app.schemas.routes import Route
from app.services.utils  import run_command

logger = logging.getLogger(__name__)


# def load_stored_routes_to_system() -> None:
#     """
#     Load active routes from the database and applies them to the system.
#     """
#     logger.info("Loading active routes from database")
#     try:
#         database_routes: list = get_routes_from_database()
#     db: Session = SessionLocal()
#     try:
#         now = datetime.now(datetime.timezone.utc)
#         stored_routes = db.query(DBRoute).all()

#         for db_route in stored_routes:
#             try:
#                 route = Route.model_validate(db_route)

#                 if route.delete_at and route.delete_at < now:
#                     delete_route(route)
#                     break
#                 else:
#                     add_route(route)

#             except Exception as e:
#                 logger.error(f"Error processing route {db_route}: {e}")

#     except Exception as e:
#         logger.error(f"Error loading routes from database: {e}")
#     finally:
#         db.close()


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
