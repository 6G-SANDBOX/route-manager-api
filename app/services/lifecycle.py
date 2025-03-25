import asyncio
import logging
from datetime import datetime, timezone
from app.services.routes import add_route_to_system, delete_route_from_system
from app.db.routes import (get_routes_from_database, delete_route_from_database, activate_route_in_database, deactivate_route_in_database, update_route_status)
from app.schemas.routes import Route
from app.core.config import settings

logger = logging.getLogger(__name__)

async def route_manager_loop():
    """
    Background task that continuously checks and updates the routing system.
    It activates or deletes routes based on their create_at and delete_at timestamps.
    """
    while True:
        try:
            database_routes = get_routes_from_database()
        except Exception as e:
            logger.error(f"Error fetching routes in lifecycle: {str(e)}")
            await asyncio.sleep(settings.ROUTE_CHECK_INTERVAL)
            continue 

        now = datetime.now(timezone.utc)

        for route in database_routes:
            # If `delete_at` is set and expired, remove the route  
            if route["delete_at"] and datetime.fromisoformat(route["delete_at"]) <= now and route["status"] != "expired":
                logger.info(f"Deleting expired route: {route['to']}")
                try:
                    delete_route_from_database(route["to"], "expired")

                    if route["status"] != "paused":
                        logger.info(f"Removing route {route['to']} from system (status is not 'paused')")
                        delete_route_from_system(route["to"])
                    else:
                        logger.info(f"Route {route['to']} was paused, so not removing from system")

                    deactivate_route_in_database(route["to"])
                except Exception as e:
                    logger.error(f"Error deleting route {route['to']}: {e}")

            # If `create_at` is set, expired, but not yet active, activate it
            elif (route["create_at"] and datetime.fromisoformat(route["create_at"]) <= now and (not route["delete_at"] or datetime.fromisoformat(route["delete_at"]) > now) and not route["active"] and route["status"] != "paused"):
                logger.info(f"Activating scheduled route: {route['to']}")
                try:
                    if activate_route_in_database(route["to"]):
                        update_route_status(route["to"], "active")
                        route_obj = Route(**route)
                        add_route_to_system(route_obj)
                except Exception as e:
                    logger.error(f"Error activating route {route['to']}: {e}")

        await asyncio.sleep(settings.ROUTE_CHECK_INTERVAL)
