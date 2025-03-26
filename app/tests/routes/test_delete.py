from app.core.config import settings
from datetime import datetime, timedelta, timezone
import json


def test_delete_route(client, auth_header):
    now = datetime.now(timezone.utc)
    payload = {
        "to": "10.10.10.0/24",
        "via": "192.168.1.1",
        "create_at": (now + timedelta(seconds=5)).isoformat(),
        "delete_at": (now + timedelta(minutes=1)).isoformat()
    }
    client.put("/routes/", json=payload, headers=auth_header)

    response = client.request(
        method="DELETE",
        url="/routes/",
        json={"to": "10.10.10.0/24"},
        headers=auth_header
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Route succesfully deleted"}

    get_response = client.get("/routes", headers=auth_header)
    assert get_response.status_code == 200

    data = get_response.json()
    routes = data["database_routes"]
    assert all(route["to"] != "10.10.10.0/24" for route in routes)


def test_delete_pending_route(client, auth_header):
    now = datetime.now(timezone.utc)
    payload = {
        "to": "10.50.50.0/24",
        "dev": "eth0",
        "create_at": (now + timedelta(minutes=5)).isoformat(),
        "delete_at": (now + timedelta(minutes=10)).isoformat()
    }

    res = client.put("/routes/", json=payload, headers=auth_header)
    assert res.status_code == 201

    res = client.request("DELETE", "/routes/", json={"to": "10.50.50.0/24"}, headers=auth_header)
    assert res.status_code == 200
    assert res.json() == {"message": "Route succesfully deleted"}

    # Verify that it is not in /routes
    res = client.get("/routes", headers=auth_header)
    assert all(r["to"] != "10.50.50.0/24" for r in res.json()["database_routes"])

    # Verify that it is in /routes/deleted
    res = client.get("/routes/deleted", headers=auth_header)
    assert any(r["to"] == "10.50.50.0/24" for r in res.json()["deleted_routes"])


def test_delete_active_route(client, auth_header):
    now = datetime.now(timezone.utc)
    payload = {
        "to": "10.60.60.0/24",
        "dev": "eth0",
        "create_at": now.isoformat(),
        "delete_at": (now + timedelta(minutes=2)).isoformat()
    }

    res = client.put("/routes/", json=payload, headers=auth_header)
    assert res.status_code == 201

    res = client.request("DELETE", "/routes/", json={"to": "10.60.60.0/24"}, headers=auth_header)
    assert res.status_code == 200
    assert res.json() == {"message": "Route succesfully deleted"}

    res = client.get("/routes", headers=auth_header)
    assert all(r["to"] != "10.60.60.0/24" for r in res.json()["database_routes"])

    res = client.get("/routes/deleted", headers=auth_header)
    assert any(r["to"] == "10.60.60.0/24" for r in res.json()["deleted_routes"])


def test_delete_nonexistent_route(client, auth_header):
    res = client.request("DELETE", "/routes/", json={"to": "192.0.2.0/24"}, headers=auth_header)
    assert res.status_code == 404
    assert "not found in the database" in res.json()["detail"]
