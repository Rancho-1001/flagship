"""
Tests for authentication.
"""
import pytest


def test_health_check_no_auth(client):
    """Test that health check doesn't require authentication."""
    response = client.get("/health")
    assert response.status_code == 200


def test_protected_endpoint_without_api_key(client, sample_flag_data):
    """Test that protected endpoints require API key."""
    response = client.post("/flags", json=sample_flag_data)
    assert response.status_code == 401
    assert "api key" in response.json()["detail"].lower()


def test_protected_endpoint_with_invalid_api_key(client, sample_flag_data, auth_headers):
    """Test that invalid API keys are rejected."""
    invalid_headers = {"X-API-Key": "invalid-key"}
    response = client.post("/flags", json=sample_flag_data, headers=invalid_headers)
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


def test_protected_endpoint_with_valid_api_key(client, sample_flag_data, auth_headers):
    """Test that valid API keys are accepted."""
    response = client.post("/flags", json=sample_flag_data, headers=auth_headers)
    assert response.status_code == 201

