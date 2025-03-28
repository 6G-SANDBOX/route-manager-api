# app/db/routes.py
import logging
import json
from datetime import datetime, timezone
from sqlmodel import Session, select
from app.db.database import engine
from app.db.models.routes import DBRoute
from app.db.models.deleted_routes import DeletedRoute
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

def add_route_to_database(route: Route, active: bool, status: str) -> bool:
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
            active=active,
            status=status
        )
        session.add(db_route)

    logger.info(f"Route to {route.to} added to database successfully")
    return True


def delete_route_from_database(to: str,  status: str) -> bool:
    """
    Deletes a route from the database.

    Args:
        to (str): The destination IP Address/Network of the route to delete.

    Returns:
        bool: True if the route was active in the system, False otherwise.
    """
    logger.info("Deleting route from database...")
    with Session(engine) as session, session.begin():
        statement = select(DBRoute).where(DBRoute.to == to)
        db_route = session.exec(statement).one()

        # Store in Deleted_Routes before removing from main table
        store_deleted_route_in_database(db_route, status=status)

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


def deactivate_route_in_database(to: str) -> bool:
    """
    Updates the 'active' field of a route in the database to False.

    Args:
        to (str): The destination IP Address/Network of the route to deactivate.

    Returns:
        bool: True if the route was found and updated, False otherwise.
    """
    logger.info(f"Deactivating route {to} in the database...")

    with Session(engine) as session, session.begin():
        statement = select(DBRoute).where(DBRoute.to == to)
        db_route = session.exec(statement).one_or_none()

        if not db_route:
            logger.warning(f"Route {to} not found in the database.")
            return False

        db_route.active = False  # 🔹 Cambiamos active a False
        session.add(db_route)
        session.commit()

    logger.info(f"Route {to} deactivated successfully in the database.")
    return True


def update_route_status(to: str, new_status: str) -> bool:
    """
    Updates the 'status' field of a route in the database.

    Args:
        to (str): The destination IP Address/Network of the route to update.
        new_status (str): The new status to set ('active', 'pending', 'expired').

    Returns:
        bool: True if the route was found and updated, False otherwise.
    """
    logger.info(f"Updating status of route {to} to '{new_status}' in the database...")

    with Session(engine) as session, session.begin():
        statement = select(DBRoute).where(DBRoute.to == to)
        db_route = session.exec(statement).one_or_none()

        if not db_route:
            logger.warning(f"Route {to} not found in the database.")
            return False

        db_route.status = new_status
        session.add(db_route)
        session.commit()

    logger.info(f"Route {to} status updated successfully to '{new_status}'.")
    return True
    

def update_route_in_database(to: str, route_update: Route) -> bool:
    """
    Updates an existing route in the database with new values, ensuring:
    - 'via' and 'dev' are mutually exclusive (if one is updated, the other is removed).
    - 'create_at' and 'delete_at' can be updated separately.
    
    Args:
        to (str): The destination IP Address/Network of the route to update.
        route_update (Route): The new data for the route.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    logger.info(f"Updating route {to} in the database...")

    with Session(engine) as session, session.begin():
        statement = select(DBRoute).where(DBRoute.to == to)
        db_route = session.exec(statement).one_or_none()

        if not db_route:
            logger.warning(f"Route {to} not found in the database.")
            return False

        # Overwrite "via" and "dev" together (if updating one, clear the other)
        if route_update.via is not None:
            db_route.via = str(route_update.via)
            db_route.dev = None  # Remove dev if via is updated
        elif route_update.dev is not None:
            db_route.dev = route_update.dev
            db_route.via = None  # Remove via if dev is updated

        # Allow separate updates for create_at and delete_at
        if route_update.create_at is not None:
            db_route.create_at = route_update.create_at
        if route_update.delete_at is not None:
            db_route.delete_at = route_update.delete_at

        # Default values: Let lifecycle manage activation
        db_route.status = "pending"
        db_route.active = False

        session.add(db_route)
        session.commit()

    logger.info(f"Route {to} successfully updated in the database.")
    return True


def store_deleted_route_in_database(route: DBRoute, status: str) -> None:
    """
    Stores a deleted route in the deleted routes table.
    """
    logger.info(f"Storing deleted route {route.to} in Deleted_Routes table...")

    deleted_route = DeletedRoute(
        to=route.to,
        via=route.via,
        dev=route.dev,
        create_at=route.create_at,
        delete_at=route.delete_at,
        status=status
    )

    try:
        with Session(engine) as session, session.begin():
            session.add(deleted_route)
            logger.info(f"Route {deleted_route.to} successfully added to Deleted_Routes with status '{status}'")
    except Exception as e:
        logger.error(f"Failed to store route {route.to} in Deleted_Routes: {e}")



def get_deleted_routes_from_database() -> list[dict]:
    """
    Fetches all deleted routes from the Deleted_Routes table.

    Returns:
        list[dict]: A list of JSON dictionaries representing deleted routes.
    """
    logger.info("Fetching deleted routes from database...")

    with Session(engine) as session, session.begin():
        deleted_routes = session.exec(select(DeletedRoute)).all()

        serialized_routes: list[dict] = []
        for route in deleted_routes:
            route_dict = json.loads(route.model_dump_json())
            route_dict["removed_at"] = datetime.fromisoformat(route_dict["removed_at"]).astimezone(timezone.utc).isoformat()

            serialized_routes.append(route_dict)

    logger.info("Deleted routes fetched successfully")
    return serialized_routes
