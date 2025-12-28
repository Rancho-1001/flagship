"""
Tests for API endpoints.
"""
import pytest
from app.schemas import FeatureFlagCreate


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert data["service"] == "FlagShip"
    assert "database" in data


def test_create_flag(client, sample_flag_data, auth_headers):
    """Test creating a feature flag via API."""
    response = client.post("/flags", json=sample_flag_data, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == sample_flag_data["name"]
    assert data["environment"] == sample_flag_data["environment"]
    assert data["enabled"] == sample_flag_data["enabled"]
    assert data["rollout"] == sample_flag_data["rollout"]
    assert "id" in data
    assert "updated_at" in data


def test_create_duplicate_flag(client, sample_flag_data, auth_headers):
    """Test that creating a duplicate flag returns 400."""
    client.post("/flags", json=sample_flag_data, headers=auth_headers)
    
    # Try to create duplicate
    response = client.post("/flags", json=sample_flag_data, headers=auth_headers)
    assert response.status_code == 400
    assert "already exists" in response.json()["error"].lower()


def test_create_flag_invalid_rollout(client, sample_flag_data, auth_headers):
    """Test creating a flag with invalid rollout value."""
    invalid_data = sample_flag_data.copy()
    invalid_data["rollout"] = 150  # Invalid: > 100
    
    response = client.post("/flags", json=invalid_data, headers=auth_headers)
    assert response.status_code == 422  # Validation error


def test_get_flag(client, sample_flag_data, auth_headers):
    """Test getting a specific flag."""
    # Create flag first
    create_response = client.post("/flags", json=sample_flag_data, headers=auth_headers)
    assert create_response.status_code == 201
    
    # Get the flag
    response = client.get(
        f"/flags/{sample_flag_data['name']}",
        params={"environment": sample_flag_data["environment"]},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == sample_flag_data["name"]
    assert data["environment"] == sample_flag_data["environment"]


def test_get_nonexistent_flag(client, auth_headers):
    """Test getting a flag that doesn't exist."""
    response = client.get(
        "/flags/nonexistent",
        params={"environment": "dev"},
        headers=auth_headers
    )
    assert response.status_code == 404
    assert "not found" in response.json()["error"].lower()


def test_list_flags(client, sample_flag_data, auth_headers):
    """Test listing all flags."""
    # Create a flag
    client.post("/flags", json=sample_flag_data, headers=auth_headers)
    
    # List all flags
    response = client.get("/flags", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "flags" in data
    assert "total" in data
    assert len(data["flags"]) >= 1
    assert data["total"] >= 1


def test_list_flags_filtered(client, sample_flag_data, auth_headers):
    """Test listing flags filtered by environment."""
    # Create flags in different environments
    dev_flag = sample_flag_data.copy()
    staging_flag = sample_flag_data.copy()
    staging_flag["environment"] = "staging"
    
    client.post("/flags", json=dev_flag, headers=auth_headers)
    client.post("/flags", json=staging_flag, headers=auth_headers)
    
    # List dev flags only
    response = client.get("/flags", params={"environment": "dev"}, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert all(flag["environment"] == "dev" for flag in data["flags"])


def test_list_flags_pagination(client, auth_headers):
    """Test pagination in list endpoint."""
    # Create multiple flags
    for i in range(5):
        flag_data = {
            "name": f"flag{i}",
            "environment": "dev",
            "enabled": True,
            "rollout": 100
        }
        client.post("/flags", json=flag_data, headers=auth_headers)
    
    # Test pagination
    response = client.get("/flags", params={"skip": 0, "limit": 2}, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["flags"]) == 2


def test_update_flag(client, sample_flag_data, auth_headers):
    """Test updating a feature flag."""
    # Create flag first
    create_response = client.post("/flags", json=sample_flag_data, headers=auth_headers)
    assert create_response.status_code == 201
    
    # Update the flag
    update_data = {"enabled": False, "rollout": 50}
    response = client.put(
        f"/flags/{sample_flag_data['name']}",
        params={"environment": sample_flag_data["environment"]},
        json=update_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["enabled"] is False
    assert data["rollout"] == 50


def test_update_nonexistent_flag(client, auth_headers):
    """Test updating a flag that doesn't exist."""
    update_data = {"enabled": False}
    response = client.put(
        "/flags/nonexistent",
        params={"environment": "dev"},
        json=update_data,
        headers=auth_headers
    )
    assert response.status_code == 404


def test_delete_flag(client, sample_flag_data, auth_headers):
    """Test deleting a feature flag."""
    # Create flag first
    client.post("/flags", json=sample_flag_data, headers=auth_headers)
    
    # Delete the flag
    response = client.delete(
        f"/flags/{sample_flag_data['name']}",
        params={"environment": sample_flag_data["environment"]},
        headers=auth_headers
    )
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = client.get(
        f"/flags/{sample_flag_data['name']}",
        params={"environment": sample_flag_data["environment"]},
        headers=auth_headers
    )
    assert get_response.status_code == 404


def test_delete_nonexistent_flag(client, auth_headers):
    """Test deleting a flag that doesn't exist."""
    response = client.delete(
        "/flags/nonexistent",
        params={"environment": "dev"},
        headers=auth_headers
    )
    assert response.status_code == 404

