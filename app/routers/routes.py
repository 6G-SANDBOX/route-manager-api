# app/routers/routes.py
import logging
import json
import subprocess
from typing import Annotated
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.services.auth import bearer_token
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from pydantic import IPvAnyNetwork
from app.schemas.routes  import Route
from app.services.routes import add_route_to_system, delete_route_from_system
from app.db.routes        import get_routes_from_database, add_route_to_database, delete_route_from_database
from app.services.utils  import run_command

logger = logging.getLogger(__name__)
routes = APIRouter(prefix="/routes", tags=["routes"])


@routes.get("/", dependencies=[Depends(bearer_token)])
def routes_get() -> dict[str, list]:
    """
    Fetches all active routes using the `ip route show` command.

    Returns:
        `dict[str, list[str]]`: A Diccionary with key word "routes" and a list of active routes as value
    """
    logger.info("GET REQUEST RECEIVED")
    try:
        database_routes: list[dict] = get_routes_from_database()
    except:
        raise HTTPException(status_code=500, detail="Error fetching routes from database")
    else:
        try:
            system_routes: str = run_command(["ip", "route", "show"])
        except subprocess.CalledProcessError as e:
            raise HTTPException(status_code=500, detail=f"{e.stderr.strip()}")
    
    return JSONResponse(
        content={
            "database_routes": database_routes,
            "system_routes": [s.strip() for s in system_routes.splitlines()]
        },
        status_code=200
    )


@routes.put("/", dependencies=[Depends(bearer_token)])
def routes_put(route: Route) -> dict[str, str]:
    """
    Schedules a new route to be added to the system and the database

    Args:
        `route (Route)`: A Route object containing to, via, dev, create_at, and delete_at.

    Returns:
       `dict[str, str]`: Success message indicating the route was scheduled.
    """
    logger.info("PUT REQUEST RECEIVED")

    if route.create_at > datetime.now(timezone.utc):
        try:
            add_route_to_database(route, active=False)
        except IntegrityError:
            logger.warning(f"Route to {route.to} already exists in the database.")
            raise HTTPException(status_code=409, detail=f"A route to {route.to} already exists in the database.")
        except SQLAlchemyError as e:
            logger.error(f"Database error while adding route: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database error while adding route: {str(e)}")
    else:
        try:
            add_route_to_system(route)
            add_route_to_database(route, active=True)
        except subprocess.CalledProcessError as e:
            if "RTNETLINK answers: File exists" in e.stderr.strip():
                return JSONResponse(
                    content={"message": f"A route to {route.to} already exists in the system"},
                    status_code=200
                )
            raise HTTPException(status_code=500, detail=f"{e.stderr.strip()}")

    return JSONResponse(
        content={"message": "Route succesfully added or scheduled"},
        status_code=201
    )


@routes.delete("/", dependencies=[Depends(bearer_token)])
def routes_delete(to: Annotated[IPvAnyNetwork, Body(embed=True)]) -> dict[str, str]:
    """
    Removes an existing route from the system and the database

    Args:
        to (IPvAnyNetwork): The destination IP Address/Network of the route to remove.

    Returns:
        dict[str, str]: A success message indicating the route was removed.
    """
    logger.info("DELETE REQUEST RECEIVED")
    try:
        active: bool = delete_route_from_database(str(to))
    except NoResultFound:
        logger.warning(f"Route to {to} not found in the database.")
        raise HTTPException(status_code=404, detail=f"Route to {to} not found in the database.")
    except MultipleResultsFound:
        logger.warning(f"More than one to {to} exists in the database. Please remove one manually.")
        raise HTTPException(status_code=409, detail=f"More than one to {to} exists in the database. Please remove one manually.")
    except SQLAlchemyError as e:
        logger.error(f"Database error while deleting route: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error while deleting route: {str(e)}")
    else:
        if active:
            try:
                delete_route_from_system(str(to))
            except subprocess.CalledProcessError as e:
                raise HTTPException(status_code=500, detail=f"{e.stderr.strip()}")
            
    return JSONResponse(
        content={"message": "Route succesfully deleted"},
        status_code=200
    )
