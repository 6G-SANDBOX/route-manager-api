import time
from datetime import datetime, timedelta, timezone
from app.db.routes import get_routes_from_database
from app.services.routes import delete_route_from_system


def test_route_manager_activates_pending_route(client, auth_header):
    now = datetime.now(timezone.utc)
    payload = {
        "to": "10.200.200.0/24",
        "dev": "eth0",
        "create_at": (now + timedelta(seconds=1)).isoformat(),
        "delete_at": (now + timedelta(minutes=1)).isoformat()
    }

    res = client.put("/routes/", json=payload, headers=auth_header)
    assert res.status_code == 201

    # Wait for the route to be activated
    time.sleep(12)

    # Verify is active
    routes = get_routes_from_database()
    route = next((r for r in routes if r["to"] == "10.200.200.0/24"), None)
    assert route is not None
    assert route["status"] == "active"
    assert route["active"] is True

    # Clean up
    delete_route_from_system("10.200.200.0/24")


def test_route_manager_expires_route(client, auth_header):
    now = datetime.now(timezone.utc)
    payload = {
        "to": "10.201.201.0/24",
        "dev": "eth0",
        "create_at": (now - timedelta(seconds=2)).isoformat(),
        "delete_at": (now + timedelta(seconds=3)).isoformat()
    }

    res = client.put("/routes/", json=payload, headers=auth_header)
    assert res.status_code == 201

    # Wait for create and delete
    time.sleep(15)

    # Verify is deleted from the system
    routes = get_routes_from_database()
    route = next((r for r in routes if r["to"] == "10.201.201.0/24"), None)
    assert route is None


def test_route_manager_does_not_activate_paused_route(client, auth_header):
    now = datetime.now(timezone.utc)
    payload = {
        "to": "10.202.202.0/24",
        "dev": "eth0",
        "create_at": (now - timedelta(seconds=10)).isoformat(),
        "delete_at": (now + timedelta(minutes=1)).isoformat()
    }

    res = client.put("/routes/", json=payload, headers=auth_header)
    assert res.status_code == 201

    # Pause the route manually
    pause_res = client.patch("/routes/pause", json={"to": "10.202.202.0/24"}, headers=auth_header)
    assert pause_res.status_code == 200

    # Wait for the route to be activated
    time.sleep(12)

    routes = get_routes_from_database()
    route = next((r for r in routes if r["to"] == "10.202.202.0/24"), None)
    assert route is not None
    assert route["status"] == "paused"
    assert route["active"] is False


def test_route_manager_keeps_route_active_without_delete_at(client, auth_header):
    now = datetime.now(timezone.utc)
    payload = {
        "to": "10.204.204.0/24",
        "dev": "eth0",
        "create_at": (now + timedelta(seconds=1)).isoformat(),
        # No delete_at
    }

    res = client.put("/routes/", json=payload, headers=auth_header)
    assert res.status_code == 201

    time.sleep(12)

    routes = get_routes_from_database()
    route = next((r for r in routes if r["to"] == "10.204.204.0/24"), None)
    assert route is not None
    assert route["status"] == "active"
    assert route["active"] is True

    delete_route_from_system("10.204.204.0/24")


def test_route_manager_does_not_delete_paused_route_from_system(client, auth_header):
    now = datetime.now(timezone.utc)
    payload = {
        "to": "10.205.205.0/24",
        "dev": "eth0",
        "create_at": (now - timedelta(minutes=1)).isoformat(),
        "delete_at": (now + timedelta(seconds=3)).isoformat()
    }

    res = client.put("/routes/", json=payload, headers=auth_header)
    assert res.status_code == 201

    pause_res = client.patch("/routes/pause", json={"to": "10.205.205.0/24"}, headers=auth_header)
    assert pause_res.status_code == 200

    time.sleep(12)

    routes = get_routes_from_database()
    route = next((r for r in routes if r["to"] == "10.205.205.0/24"), None)
    assert route is None
