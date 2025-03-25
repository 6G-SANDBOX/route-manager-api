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
from app.schemas.routes import Route, RouteUpdate
from app.services.routes import add_route_to_system, delete_route_from_system
from app.db.routes import get_routes_from_database, add_route_to_database, delete_route_from_database, update_route_in_database, get_deleted_routes_from_database, deactivate_route_in_database, update_route_status, activate_route_in_database
from app.services.utils import run_command

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

    now = datetime.now(timezone.utc)

    if route.create_at > now:
        try:
            add_route_to_database(route, active=False, status="pending")
        except IntegrityError:
            logger.warning(f"Route to {route.to} already exists in the database.")
            raise HTTPException(status_code=409, detail=f"A route to {route.to} already exists in the database.")
        except SQLAlchemyError as e:
            logger.error(f"Database error while adding route: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database error while adding route: {str(e)}")

    elif route.create_at <= now and (not route.delete_at or route.delete_at > now):
        try:
            add_route_to_system(route)
            add_route_to_database(route, active=True, status="active")
        except subprocess.CalledProcessError as e:
            if "RTNETLINK answers: File exists" in e.stderr.strip():
                return JSONResponse(
                    content={"message": f"A route to {route.to} already exists in the system"},
                    status_code=200
                )
            raise HTTPException(status_code=500, detail=f"{e.stderr.strip()}")
    
    elif route.delete_at and route.delete_at < now:
        try:
            add_route_to_database(route, active=False, status="expired")
        except IntegrityError:
            logger.warning(f"Route to {route.to} already exists in the database.")
            raise HTTPException(status_code=409, detail=f"A route to {route.to} already exists in the database.")
        except SQLAlchemyError as e:
            logger.error(f"Database error while adding route: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database error while adding route: {str(e)}")

    else:
        logger.error(f"Unexpected case for route {route.to}")
        raise HTTPException(status_code=500, detail="Unexpected error while processing route.")
    
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
        active: bool = delete_route_from_database(str(to), status="deleted")
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


@routes.patch("/", dependencies=[Depends(bearer_token)])
def routes_update(route_update: RouteUpdate) -> dict[str, str]:
    """
    Updates an existing route in the database.

    Args:
        route_update (Route): A Route object containing the fields to update.

    Returns:
        dict[str, str]: A success message if the update was successful.
    """
    logger.info(f"PATCH REQUEST RECEIVED to update route {route_update.to}")

    if update_route_in_database(str(route_update.to), route_update):
        return JSONResponse(
            content={"message": f"Route {route_update.to} successfully updated"},
            status_code=200
        )
    else:
        raise HTTPException(status_code=404, detail=f"Route {route_update.to} not found in the database.")
    

@routes.get("/deleted", dependencies=[Depends(bearer_token)])
def deleted_routes_get() -> dict[str, list]:
    """
    Fetches all deleted routes from the database.

    Returns:
        dict[str, list]: A dictionary with key "deleted_routes" and a list of deleted routes as value.
    """
    logger.info("GET REQUEST RECEIVED for deleted routes")

    try:
        deleted_routes: list[dict] = get_deleted_routes_from_database()
    except Exception as e:
        logger.error(f"Error fetching deleted routes: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching deleted routes from database")

    return JSONResponse(
        content={"deleted_routes": deleted_routes},
        status_code=200
    )

@routes.patch("/pause", dependencies=[Depends(bearer_token)])
def pause_route(to: Annotated[IPvAnyNetwork, Body(embed=True)]) -> dict[str, str]:
    """
    Pauses an active route by deactivating it in the database and removing it from the system.

    Args:
        to (IPvAnyNetwork): The destination network of the route to pause.

    Returns:
        dict[str, str]: A success message if the pause was successful.
    """
    logger.info(f"PATCH REQUEST RECEIVED to pause route {to}")

    try:
        database_routes = get_routes_from_database()
        route = next((r for r in database_routes if r["to"] == str(to)), None)

        if not route:
            raise HTTPException(status_code=404, detail=f"Route {to} not found in the database.")

        now = datetime.now(timezone.utc)
        is_active_period = route["create_at"] and datetime.fromisoformat(route["create_at"]) <= now \
            and (not route["delete_at"] or datetime.fromisoformat(route["delete_at"]) > now)

        if route["status"] != "active" or not route["active"] or not is_active_period:
            raise HTTPException(status_code=409, detail=f"Route {to} is not currently active and cannot be paused.")

        # Remove from system and update DB
        delete_route_from_system(str(to))
        deactivate_route_in_database(str(to))
        update_route_status(str(to), "paused")

        return JSONResponse(
            content={"message": f"Route {to} successfully paused"},
            status_code=200
        )

    except Exception as e:
        logger.error(f"Error while pausing route {to}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while pausing route.")


@routes.patch("/activate", dependencies=[Depends(bearer_token)])
def activate_route(to: Annotated[IPvAnyNetwork, Body(embed=True)]) -> dict[str, str]:
    """
    Reactivates a paused route by setting it to active in the database and applying it to the system.

    Args:
        to (IPvAnyNetwork): The destination network of the route to activate.

    Returns:
        dict[str, str]: A success message if the activation was successful.
    """
    logger.info(f"PATCH REQUEST RECEIVED to activate route {to}")

    try:
        database_routes = get_routes_from_database()
        route = next((r for r in database_routes if r["to"] == str(to)), None)

        if not route:
            raise HTTPException(status_code=404, detail=f"Route {to} not found in the database.")

        now = datetime.now(timezone.utc)
        is_active_period = route["create_at"] and datetime.fromisoformat(route["create_at"]) <= now \
            and (not route["delete_at"] or datetime.fromisoformat(route["delete_at"]) > now)

        if route["status"] != "paused" or route["active"] or not is_active_period:
            raise HTTPException(status_code=409, detail=f"Route {to} is not currently paused or out of active period.")

        # Add to system and update DB
        route_obj = Route(**route)
        add_route_to_system(route_obj)
        activate_route_in_database(str(to))
        update_route_status(str(to), "active")

        return JSONResponse(
            content={"message": f"Route {to} successfully re-activated"},
            status_code=200
        )

    except subprocess.CalledProcessError as e:
        logger.error(f"System error while activating route {to}: {e.stderr.strip()}")
        raise HTTPException(status_code=500, detail=f"System error: {e.stderr.strip()}")

    except Exception as e:
        logger.error(f"Unexpected error while activating route {to}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while activating route.")
