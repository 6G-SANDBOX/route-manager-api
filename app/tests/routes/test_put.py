from app.core.config import settings
from datetime import datetime, timedelta, timezone
import json


def test_put_route(client, auth_header):
    now = datetime.now(timezone.utc)
    payload = {
        "to": "10.10.10.0/24",
        "via": "192.168.1.1",
        "create_at": (now + timedelta(seconds=5)).isoformat(),
        "delete_at": (now + timedelta(minutes=1)).isoformat()
    }

    # PUT route
    response = client.put("/routes/", json=payload, headers=auth_header)
    assert response.status_code == 201
    assert "message" in response.json()

    # Verify route was added
    response = client.get("/routes", headers=auth_header)
    assert response.status_code == 200

    data = response.json()
    assert any(route["to"] == "10.10.10.0/24" for route in data["database_routes"])


def test_put_multiple_routes_should_fail(client, auth_header):
    now = datetime.now(timezone.utc).isoformat()
    delete_later = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()

    payload = [
        {
            "to": "10.10.20.0/24",
            "dev": "eth0",
            "create_at": now,
            "delete_at": delete_later
        },
        {
            "to": "10.10.21.0/24",
            "dev": "eth0",
            "create_at": now,
            "delete_at": delete_later
        }
    ]

    response = client.put("/routes/", json=payload, headers=auth_header)

    assert response.status_code == 422  # Unprocessable Entity
    data = response.json()

    assert data["detail"][0]["type"] == "model_attributes_type"
    assert data["detail"][0]["loc"] == ["body"]
    assert (
        data["detail"][0]["msg"]
        == "Input should be a valid dictionary or object to extract fields from"
    )

def test_put_route_without_delete_at(client, auth_header):
    now = datetime.now(timezone.utc)
    payload = {
        "to": "10.3.3.0/24",
        "via": "192.168.1.1",
        "create_at": (now + timedelta(seconds=10)).isoformat()
    }

    res = client.put("/routes/", json=payload, headers=auth_header)
    assert res.status_code == 201


def test_put_invalid_missing_via_and_dev(client, auth_header):
    now = datetime.now(timezone.utc)
    payload = {
        "to": "10.4.4.0/24",
        "create_at": now.isoformat(),
        "delete_at": (now + timedelta(minutes=1)).isoformat()
    }

    res = client.put("/routes/", json=payload, headers=auth_header)
    assert res.status_code == 422
    assert "Route must include at least one of 'via' or 'dev'" in res.text


def test_put_invalid_dev_not_exists(client, auth_header):
    now = datetime.now(timezone.utc)
    payload = {
        "to": "10.5.5.0/24",
        "dev": "fake0",
        "create_at": now.isoformat(),
        "delete_at": (now + timedelta(minutes=1)).isoformat()
    }

    res = client.put("/routes/", json=payload, headers=auth_header)
    assert res.status_code == 422
    assert "is not a valid network interface" in res.text


def test_put_invalid_create_at_no_tz(client, auth_header):
    now = datetime.utcnow().replace(tzinfo=None)  # sin timezone
    payload = {
        "to": "10.6.6.0/24",
        "via": "192.168.1.1",
        "create_at": now.isoformat(),
        "delete_at": (datetime.now(timezone.utc) + timedelta(minutes=1)).isoformat()
    }

    res = client.put("/routes/", json=payload, headers=auth_header)
    assert res.status_code == 422
    assert "must include timezone information" in res.text


def test_put_invalid_delete_at_in_past(client, auth_header):
    now = datetime.now(timezone.utc)
    payload = {
        "to": "10.7.7.0/24",
        "via": "192.168.1.1",
        "create_at": now.isoformat(),
        "delete_at": (now - timedelta(minutes=1)).isoformat()
    }

    res = client.put("/routes/", json=payload, headers=auth_header)
    assert res.status_code == 422
    assert "has already passed" in res.text


def test_put_invalid_delete_at_before_create_at(client, auth_header):
    now = datetime.now(timezone.utc)
    payload = {
        "to": "10.8.8.0/24",
        "via": "192.168.1.1",
        "create_at": (now + timedelta(minutes=2)).isoformat(),
        "delete_at": (now + timedelta(minutes=1)).isoformat()
    }

    res = client.put("/routes/", json=payload, headers=auth_header)
    assert res.status_code == 422
    assert "can't be set before create_at" in res.text
