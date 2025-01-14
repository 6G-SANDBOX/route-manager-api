# app/routers/routes.py
import logging
from typing import Dict, List
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.routes import Route
from app.services.routes import (
    get_active_routes,
    schedule_add_route,
    delete_route
)
from app.services.auth import auth


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/routes", tags=["routes"])


@router.get("/", dependencies=[Depends(auth)])
def routes_get() -> Dict[str, List[str]]:
    """
    Fetches all active routes.

    Returns:
        Dict[str, list[str]]: A Diccionary with key word "routes" and a list of active routes as value
    """
    logger.info("Fetching active routes")
    return get_active_routes()


@router.post("/", dependencies=[Depends(auth)])
def routes_post(route: Route) -> Dict[str, str]:
    """
    Schedules a new route to be added.

    Args:
        route (Route): The route to schedule

    Returns:
        dict[str, str]: Success message indicating the route was scheduled.
    """
    try:
        schedule_add_route(route)
        return {"message": "Route successfully added or scheduled"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error scheduling route: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

@router.delete("/", dependencies=[Depends(auth)])
def routes_delete(route: Route) -> Dict[str, str]:
    """
    Removes an existing route.

    Args:
        route (Route): The route to remove.

    Returns:
        dict[str, str]: A success message indicating the route was removed.
    """
    try:
        delete_route(route)
        return {"message": "Route deleted and removed from schedule"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error deleting route: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
