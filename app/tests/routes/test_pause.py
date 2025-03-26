from app.core.config import settings
from datetime import datetime, timedelta, timezone
import json
from app.services.routes import delete_route_from_system

def test_pause_active_route(client, auth_header):
    now = datetime.now(timezone.utc)
    payload = {
        "to": "10.100.100.0/24",
        "dev": "eth0",
        "create_at": (now - timedelta(seconds=5)).isoformat(),
        "delete_at": (now + timedelta(minutes=1)).isoformat()
    }

    res = client.put("/routes/", json=payload, headers=auth_header)
    assert res.status_code == 201

    # Pause route
    res = client.patch("/routes/pause", json={"to": "10.100.100.0/24"}, headers=auth_header)
    assert res.status_code == 200
    assert res.json() == {"message": "Route 10.100.100.0/24 successfully paused"}

    # Verify route was paused
    get_res = client.get("/routes", headers=auth_header)
    data = get_res.json()
    paused_route = next((r for r in data["database_routes"] if r["to"] == "10.100.100.0/24"), None)

    assert paused_route is not None
    assert paused_route["status"] == "paused"
    assert paused_route["active"] is False


def test_pause_nonexistent_route(client, auth_header):
    res = client.patch("/routes/pause", json={"to": "192.0.2.0/24"}, headers=auth_header)
    assert res.status_code == 500
    assert res.json()["detail"] == "Internal server error while pausing route."



def test_pause_inactive_time_window(client, auth_header):
    now = datetime.now(timezone.utc)
    payload = {
        "to": "10.110.110.0/24",
        "dev": "eth0",
        "create_at": (now + timedelta(minutes=1)).isoformat(),  # future
        "delete_at": (now + timedelta(minutes=2)).isoformat()
    }

    res = client.put("/routes/", json=payload, headers=auth_header)
    assert res.status_code == 201

    pause_res = client.patch("/routes/pause", json={"to": "10.110.110.0/24"}, headers=auth_header)
    assert pause_res.status_code == 500
    assert pause_res.json()["detail"] == "Internal server error while pausing route."


def test_pause_route_unauthorized(client):
    res = client.patch("/routes/pause", json={"to": "10.1.1.0/24"})
    assert res.status_code == 403


def test_activate_paused_route(client, auth_header):
    now = datetime.now(timezone.utc)
    payload = {
        "to": "10.120.120.0/24",
        "dev": "eth0",
        "create_at": (now - timedelta(seconds=5)).isoformat(),
        "delete_at": (now + timedelta(minutes=1)).isoformat()
    }

    # Add route and pause it
    res = client.put("/routes/", json=payload, headers=auth_header)
    assert res.status_code == 201

    pause_res = client.patch("/routes/pause", json={"to": "10.120.120.0/24"}, headers=auth_header)
    assert pause_res.status_code == 200

    # Now activate it
    activate_res = client.patch("/routes/activate", json={"to": "10.120.120.0/24"}, headers=auth_header)
    assert activate_res.status_code == 200
    assert activate_res.json() == {"message": "Route 10.120.120.0/24 successfully re-activated"}

    # Verify activation
    get_res = client.get("/routes", headers=auth_header)
    data = get_res.json()
    route = next((r for r in data["database_routes"] if r["to"] == "10.120.120.0/24"), None)

    assert route is not None
    assert route["status"] == "active"
    assert route["active"] is True

    # Cleanup system route
    delete_route_from_system("10.120.120.0/24")


def test_activate_nonexistent_route(client, auth_header):
    res = client.patch("/routes/activate", json={"to": "203.0.113.0/24"}, headers=auth_header)
    assert res.status_code == 500
    assert res.json()["detail"] == "Internal server error while activating route."


def test_activate_unpaused_route(client, auth_header):
    now = datetime.now(timezone.utc)
    payload = {
        "to": "10.130.130.0/24",
        "dev": "eth0",
        "create_at": (now - timedelta(seconds=5)).isoformat(),
        "delete_at": (now + timedelta(minutes=1)).isoformat()
    }

    res = client.put("/routes/", json=payload, headers=auth_header)
    assert res.status_code == 201

    # Try to activate without pausing first
    activate_res = client.patch("/routes/activate", json={"to": "10.130.130.0/24"}, headers=auth_header)
    assert activate_res.status_code == 500
    assert activate_res.json()["detail"] == "Internal server error while activating route."

    # Cleanup system route
    delete_route_from_system("10.130.130.0/24")


def test_activate_route_unauthorized(client):
    res = client.patch("/routes/activate", json={"to": "10.1.1.0/24"})
    assert res.status_code == 403

