# app/routers/routes.py
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from app.schemas import Route
from app.models import RouteModel
from app.database import SessionLocal
from app.auth import auth
from app.utils import run_command, route_exists
from app.scheduler import add_job
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/routes", dependencies=[Depends(auth)])
def get_routes():
    logger.info("Fetching active routes")
    command = "ip route show"
    output = run_command(command)
    return {"routes": [s.strip() for s in output.splitlines()]}

@router.post("/routes", dependencies=[Depends(auth)])
def schedule_route(route: Route):
    db = SessionLocal()
    try:
        now = datetime.now()
        logger.info(f"Scheduling route: {route}")

        if route_exists(route.destination, route.gateway, route.interface):
            logger.warning(f"Route already exists: {route}")
            raise HTTPException(status_code=400, detail="Route already exists")

        if route.create_at and (route.create_at > now):
            add_job(add_route, 'date', run_date=route.create_at, args=[route])
        else:
            add_route(route)

        if route.delete_at and (route.delete_at > now):
            add_job(delete_route, 'date', run_date=route.delete_at, args=[route])

        # Guardar en la base de datos
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

        return {"message": "Route scheduled successfully"}
    except Exception as e:
        logger.error(f"Error scheduling route: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        db.close()

@router.delete("/routes", dependencies=[Depends(auth)])
def remove_scheduled_route(route: Route):
    db = SessionLocal()
    try:
        logger.info(f"Removing scheduled route: {route}")

        if not route_exists(route.destination, route.gateway, route.interface):
            logger.warning(f"Route not found: {route}")
            raise HTTPException(status_code=404, detail="Route not found")

        delete_route(route)

        # Remover de la base de datos
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

        return {"message": "Route deleted and removed from schedule"}
    except Exception as e:
        logger.error(f"Error removing route: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        db.close()

def add_route(route: Route):
    from app.utils import run_command  # Evitar importaciones circulares
    logger = logging.getLogger(__name__)
    logger.info(f"Adding route: {route}")
    command = f"ip route add {route.destination}"
    if route.gateway:
        command += f" via {route.gateway}"
    if route.interface:
        command += f" dev {route.interface}"
    run_command(command)
    logger.info("Route added successfully")

def delete_route(route: Route):
    from app.utils import run_command  # Evitar importaciones circulares
    logger = logging.getLogger(__name__)
    logger.info(f"Deleting route: {route}")
    command = f"ip route del {route.destination}"
    if route.gateway:
        command += f" via {route.gateway}"
    if route.interface:
        command += f" dev {route.interface}"
    run_command(command)
    logger.info("Route deleted successfully")
