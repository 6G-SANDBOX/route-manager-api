# app/db/routes.py
import logging
import json
from datetime import datetime, timezone
from sqlmodel import Session, select
from app.db.database import engine
from app.db.models.routes import DBRoute
from app.schemas.routes import Route

logger = logging.getLogger(__name__)

def get_routes_from_database() -> list[dict]:
    """
    Fetches all routes from the database.

    Returns:
        list[json]: A list of JSON dictionaries corresponding to each stored route.
    """
    logger.info("Fetching routes from database...")

    with Session(engine) as session, session.begin():
    # inner context calls session.commit(), if there were no exceptions
    # outer context calls session.close()
        db_routes = session.exec(select(DBRoute)).all()

        serialized_routes: list[dict] = []
        for route in db_routes:
            route_dict = json.loads(route.model_dump_json())

            route_dict["create_at"] = datetime.fromisoformat(route_dict["create_at"]).astimezone(timezone.utc).isoformat()
            if route_dict["delete_at"]:
                route_dict["delete_at"] = datetime.fromisoformat(route_dict["delete_at"]).astimezone(timezone.utc).isoformat()

            serialized_routes.append(route_dict)

    logger.info("Routes fetched from database successfully")
    return serialized_routes

def add_route_to_database(route: Route, active: bool) -> bool:
    """
    Adds a route to the database.

    Args:
        route (Route): A Route object containing to, via, dev, create_at, and delete_at.

    Returns:
        bool: True if the route was added successfully, False otherwise.
    """
    logger.info("Adding route to database...")
    with Session(engine) as session, session.begin():
        db_route = DBRoute(
            to=str(route.to),
            via=str(route.via) if route.via else None,
            dev=route.dev,
            create_at=route.create_at,
            delete_at=route.delete_at,
            active=active
        )
        session.add(db_route)

    logger.info(f"Route to {route.to} added to database successfully")
    return True


def delete_route_from_database(to: str) -> bool:
    """
    Deletes a route from the database.

    Args:
        to (str): The destination IP Address/Network of the route to delete.

    Returns:
        bool: True if the route was active in the system, False otherwise.
    """
    logger.info("Deleting route from database...")
    with Session(engine) as session, session.begin():
        statement = select(DBRoute).where(DBRoute.to == to)                  #*
        db_route = session.exec(statement).one()

        print(db_route.active)
        session.delete(db_route)

    logger.info(f"Route to {to} deleted from database successfully")
    return db_route.active


def activate_route_in_database(to: str) -> bool:
    """
    Updates the 'active' field of a route in the database to True.

    Args:
        to (str): The destination IP Address/Network of the route to activate.

    Returns:
        bool: True if the route was found and updated, False otherwise.
    """
    logger.info(f"Activating route {to} in the database...")

    with Session(engine) as session, session.begin():
        statement = select(DBRoute).where(DBRoute.to == to)
        db_route = session.exec(statement).one_or_none()

        if not db_route:
            logger.warning(f"Route {to} not found in the database.")
            return False

        db_route.active = True
        session.add(db_route)
        session.commit()

    logger.info(f"Route {to} activated successfully in the database.")
    return True
