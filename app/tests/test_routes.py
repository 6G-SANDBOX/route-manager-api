from app.core.config import settings
from datetime import datetime, timedelta, timezone

def test_get_routes(client, auth_header):
    response = client.get("/routes", headers=auth_header)

    print("RESPONSE JSON:", response.json())

    assert response.status_code == 200

    data = response.json()

    assert "database_routes" in data
    assert "system_routes" in data

    assert isinstance(data["database_routes"], list)
    assert isinstance(data["system_routes"], list)

    if data["database_routes"]:
        route = data["database_routes"][0]
        assert "to" in route
        assert "create_at" in route

    expected_response = {
        "database_routes": [],
        "system_routes": [
            "default via 172.17.0.1 dev eth0",
            "172.17.0.0/16 dev eth0 proto kernel scope link src 172.17.0.2"
        ]
    }

    assert data == expected_response


def test_put_route(client, auth_header):
    now = datetime.now(timezone.utc)
    payload = {
        "to": "10.10.10.0/24",
        "via": "192.168.1.1",
        "create_at": (now + timedelta(seconds=5)).isoformat(),
        "delete_at": (now + timedelta(minutes=1)).isoformat()
    }

    response = client.put("/routes/", json=payload, headers=auth_header)
    assert response.status_code == 201
    assert "message" in response.json()
