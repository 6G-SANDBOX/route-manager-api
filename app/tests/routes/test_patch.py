from app.core.config import settings
from datetime import datetime, timedelta, timezone
import json


def test_patch_route(client, auth_header):
    now = datetime.now(timezone.utc)
    payload = {
        "to": "10.30.30.0/24",
        "via": "192.168.1.1",
        "create_at": (now + timedelta(minutes=1)).isoformat(),  # 👈 en el futuro
        "delete_at": (now + timedelta(minutes=2)).isoformat()
    }

    client.put("/routes/", json=payload, headers=auth_header)

    update_payload = {
        "to": "10.30.30.0/24",
        "via": "192.168.2.1"
    }

    response = client.patch("/routes/", json=update_payload, headers=auth_header)
    assert response.status_code == 200
    assert response.json() == {"message": "Route 10.30.30.0/24 successfully updated"}


def test_patch_route2(client, auth_header):
    now = datetime.now(timezone.utc)
    payload = {
        "to": "10.10.10.0/24",
        "via": "192.168.1.1",
        "create_at": (now + timedelta(seconds=5)).isoformat(),
        "delete_at": (now + timedelta(minutes=1)).isoformat()
    }
    client.put("/routes/", json=payload, headers=auth_header)

    # PATCH for change via -> dev
    update_payload = {
        "to": "10.10.10.0/24",
        "dev": "eth0"
    }

    response = client.patch("/routes/", json=update_payload, headers=auth_header)
    assert response.status_code == 200
    assert response.json() == {"message": "Route 10.10.10.0/24 successfully updated"}

    # Verify route was updated
    get_response = client.get("/routes", headers=auth_header)
    assert get_response.status_code == 200

    data = get_response.json()
    updated_route = next((r for r in data["database_routes"] if r["to"] == "10.10.10.0/24"), None)

    assert updated_route is not None
    assert updated_route["dev"] == "eth0"
    assert updated_route["via"] is None



