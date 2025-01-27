# app/db/routes.py
import logging
from sqlmodel import Session, select
from app.db.database import engine
from app.db.models.routes import DBRoute
from app.schemas.routes import Route

logger = logging.getLogger(__name__)

def get_routes_from_database() -> list[dict]:
    """
    Fetches all routes from the database.

    Returns:
        list[str]: A list of strings corresponding to each stored route.
    """
    logger.info("Fetching routes from database...")
    with Session(engine) as session, session.begin():
    # inner context calls session.commit(), if there were no exceptions
    # outer context calls session.close()
        db_routes = session.exec(select(DBRoute)).all()
        # Same as the following, but this allows to specify the parameter order
        # serialized_routes = [route.model_dump() for route in db_routes]
        serialized_routes = [
            {
                "to": route.to,
                "via": route.via,
                "dev": route.dev,
                "create_at": route.create_at,
                "delete_at": route.delete_at,
                "active": route.active
            }
            for route in db_routes
        ]
    
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
            via=str(route.via),
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
