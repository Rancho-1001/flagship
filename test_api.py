#!/usr/bin/env python3
"""
Test script for FlagShip API endpoints.
Run this after starting the Docker containers to verify all endpoints work.
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"
API_KEY = "dev-api-key-12345"  # Default API key for testing


def print_response(response: requests.Response, title: str = ""):
    """Pretty print API response."""
    print(f"\n{'='*60}")
    if title:
        print(f"{title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    print(f"{'='*60}\n")


def get_headers():
    """Get headers with API key for authenticated requests."""
    return {"X-API-Key": API_KEY}


def test_health_check():
    """Test health check endpoint."""
    print("Testing Health Check...")
    response = requests.get(f"{BASE_URL}/health")
    print_response(response, "Health Check")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("✓ Health check passed")


def test_create_flag(name: str, environment: str, enabled: bool = True, rollout: int = 100):
    """Test creating a feature flag."""
    print(f"Creating flag: {name} in {environment}...")
    payload = {
        "name": name,
        "environment": environment,
        "enabled": enabled,
        "rollout": rollout
    }
    response = requests.post(f"{BASE_URL}/flags", json=payload, headers=get_headers())
    print_response(response, f"Create Flag: {name}")
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == name
    assert data["environment"] == environment
    assert data["enabled"] == enabled
    assert data["rollout"] == rollout
    print(f"✓ Created flag: {name}")
    return data


def test_get_flag(name: str, environment: str):
    """Test getting a specific flag."""
    print(f"Getting flag: {name} in {environment}...")
    response = requests.get(f"{BASE_URL}/flags/{name}?environment={environment}", headers=get_headers())
    print_response(response, f"Get Flag: {name}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == name
    assert data["environment"] == environment
    print(f"✓ Retrieved flag: {name}")
    return data


def test_list_flags(environment: str = None):
    """Test listing all flags."""
    url = f"{BASE_URL}/flags"
    if environment:
        url += f"?environment={environment}"
    print(f"Listing flags{f' in {environment}' if environment else ''}...")
    response = requests.get(url, headers=get_headers())
    print_response(response, f"List Flags{' - ' + environment if environment else ''}")
    assert response.status_code == 200
    data = response.json()
    assert "flags" in data
    assert "total" in data
    print(f"✓ Listed {data['total']} flag(s)")
    return data


def test_update_flag(name: str, environment: str, enabled: bool = None, rollout: int = None):
    """Test updating a flag."""
    print(f"Updating flag: {name} in {environment}...")
    payload = {}
    if enabled is not None:
        payload["enabled"] = enabled
    if rollout is not None:
        payload["rollout"] = rollout
    
    response = requests.put(f"{BASE_URL}/flags/{name}?environment={environment}", json=payload, headers=get_headers())
    print_response(response, f"Update Flag: {name}")
    assert response.status_code == 200
    data = response.json()
    if enabled is not None:
        assert data["enabled"] == enabled
    if rollout is not None:
        assert data["rollout"] == rollout
    print(f"✓ Updated flag: {name}")
    return data


def test_delete_flag(name: str, environment: str):
    """Test deleting a flag."""
    print(f"Deleting flag: {name} in {environment}...")
    response = requests.delete(f"{BASE_URL}/flags/{name}?environment={environment}", headers=get_headers())
    print_response(response, f"Delete Flag: {name}")
    assert response.status_code == 204
    print(f"✓ Deleted flag: {name}")


def test_error_cases():
    """Test error handling."""
    print("\nTesting error cases...")
    
    # Test getting non-existent flag
    print("Testing 404 for non-existent flag...")
    response = requests.get(f"{BASE_URL}/flags/nonexistent?environment=dev", headers=get_headers())
    assert response.status_code == 404
    print("✓ 404 error handled correctly")
    
    # Test duplicate flag creation
    print("Testing duplicate flag creation...")
    test_create_flag("duplicate_test", "dev", enabled=True, rollout=50)
    response = requests.post(f"{BASE_URL}/flags", json={
        "name": "duplicate_test",
        "environment": "dev",
        "enabled": False,
        "rollout": 25
    }, headers=get_headers())
    assert response.status_code == 400
    print("✓ Duplicate flag error handled correctly")
    
    # Test invalid rollout
    print("Testing invalid rollout value...")
    response = requests.post(f"{BASE_URL}/flags", json={
        "name": "invalid_rollout",
        "environment": "dev",
        "enabled": True,
        "rollout": 150  # Invalid: > 100
    }, headers=get_headers())
    assert response.status_code == 422  # Validation error
    print("✓ Invalid rollout validation works")
    
    # Clean up
    test_delete_flag("duplicate_test", "dev")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("FlagShip API Test Suite")
    print("="*60 + "\n")
    
    try:
        # Test health check
        test_health_check()
        
        # Test CRUD operations
        print("\n" + "-"*60)
        print("Testing CRUD Operations")
        print("-"*60)
        
        # Create flags in different environments
        flag1 = test_create_flag("new_ui", "dev", enabled=True, rollout=100)
        flag2 = test_create_flag("new_ui", "staging", enabled=False, rollout=50)
        flag3 = test_create_flag("payment_v2", "prod", enabled=True, rollout=25)
        flag4 = test_create_flag("beta_feature", "dev", enabled=True, rollout=75)
        
        # Get specific flag
        test_get_flag("new_ui", "dev")
        
        # List all flags
        test_list_flags()
        
        # List flags by environment
        test_list_flags(environment="dev")
        test_list_flags(environment="prod")
        
        # Update flag
        test_update_flag("new_ui", "dev", enabled=False, rollout=50)
        test_get_flag("new_ui", "dev")  # Verify update
        
        # Delete flag
        test_delete_flag("beta_feature", "dev")
        
        # Verify deletion
        response = requests.get(f"{BASE_URL}/flags/beta_feature?environment=dev", headers=get_headers())
        assert response.status_code == 404
        print("✓ Deletion verified")
        
        # Test error cases
        print("\n" + "-"*60)
        print("Testing Error Handling")
        print("-"*60)
        test_error_cases()
        
        # Final cleanup
        print("\n" + "-"*60)
        print("Cleaning up test data...")
        print("-"*60)
        test_delete_flag("new_ui", "dev")
        test_delete_flag("new_ui", "staging")
        test_delete_flag("payment_v2", "prod")
        
        print("\n" + "="*60)
        print("✓ All tests passed!")
        print("="*60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API.")
        print("Make sure the Docker containers are running:")
        print("  docker-compose up -d")
        print("\n")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}\n")
        raise
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
        raise


if __name__ == "__main__":
    main()

