"""
Tests for CRUD operations.
"""
import pytest
from app.crud import (
    create_flag,
    get_flag,
    list_flags,
    count_flags,
    update_flag,
    delete_flag
)
from app.schemas import FeatureFlagCreate, FeatureFlagUpdate
from app.exceptions import FlagAlreadyExistsError, DatabaseError


def test_create_flag(db_session, sample_flag_data):
    """Test creating a feature flag."""
    flag_data = FeatureFlagCreate(**sample_flag_data)
    flag = create_flag(db_session, flag_data)
    
    assert flag.name == sample_flag_data["name"]
    assert flag.environment == sample_flag_data["environment"]
    assert flag.enabled == sample_flag_data["enabled"]
    assert flag.rollout == sample_flag_data["rollout"]
    assert flag.id is not None


def test_create_duplicate_flag(db_session, sample_flag_data):
    """Test that creating a duplicate flag raises an error."""
    flag_data = FeatureFlagCreate(**sample_flag_data)
    create_flag(db_session, flag_data)
    
    # Try to create duplicate
    with pytest.raises(FlagAlreadyExistsError):
        create_flag(db_session, flag_data)


def test_get_flag(db_session, sample_flag_data):
    """Test getting a feature flag."""
    flag_data = FeatureFlagCreate(**sample_flag_data)
    created_flag = create_flag(db_session, flag_data)
    
    retrieved_flag = get_flag(db_session, sample_flag_data["name"], sample_flag_data["environment"])
    
    assert retrieved_flag is not None
    assert retrieved_flag.id == created_flag.id
    assert retrieved_flag.name == sample_flag_data["name"]


def test_get_nonexistent_flag(db_session):
    """Test getting a flag that doesn't exist."""
    flag = get_flag(db_session, "nonexistent", "dev")
    assert flag is None


def test_list_flags(db_session):
    """Test listing all flags."""
    # Create multiple flags
    flags_data = [
        {"name": "flag1", "environment": "dev", "enabled": True, "rollout": 100},
        {"name": "flag2", "environment": "dev", "enabled": False, "rollout": 50},
        {"name": "flag1", "environment": "staging", "enabled": True, "rollout": 75},
    ]
    
    for flag_data in flags_data:
        create_flag(db_session, FeatureFlagCreate(**flag_data))
    
    # List all flags
    all_flags = list_flags(db_session)
    assert len(all_flags) == 3
    
    # List flags filtered by environment
    dev_flags = list_flags(db_session, environment="dev")
    assert len(dev_flags) == 2
    
    staging_flags = list_flags(db_session, environment="staging")
    assert len(staging_flags) == 1


def test_list_flags_pagination(db_session):
    """Test pagination in list_flags."""
    # Create 5 flags
    for i in range(5):
        flag_data = FeatureFlagCreate(
            name=f"flag{i}",
            environment="dev",
            enabled=True,
            rollout=100
        )
        create_flag(db_session, flag_data)
    
    # Test pagination
    flags = list_flags(db_session, skip=0, limit=2)
    assert len(flags) == 2
    
    flags = list_flags(db_session, skip=2, limit=2)
    assert len(flags) == 2
    
    flags = list_flags(db_session, skip=4, limit=2)
    assert len(flags) == 1


def test_count_flags(db_session):
    """Test counting flags."""
    # Create flags in different environments
    flags_data = [
        {"name": "flag1", "environment": "dev", "enabled": True, "rollout": 100},
        {"name": "flag2", "environment": "dev", "enabled": False, "rollout": 50},
        {"name": "flag1", "environment": "staging", "enabled": True, "rollout": 75},
    ]
    
    for flag_data in flags_data:
        create_flag(db_session, FeatureFlagCreate(**flag_data))
    
    # Count all flags
    total = count_flags(db_session)
    assert total == 3
    
    # Count flags by environment
    dev_count = count_flags(db_session, environment="dev")
    assert dev_count == 2
    
    staging_count = count_flags(db_session, environment="staging")
    assert staging_count == 1


def test_update_flag(db_session, sample_flag_data):
    """Test updating a feature flag."""
    flag_data = FeatureFlagCreate(**sample_flag_data)
    created_flag = create_flag(db_session, flag_data)
    
    # Update the flag
    update_data = FeatureFlagUpdate(enabled=False, rollout=50)
    updated_flag = update_flag(
        db_session,
        sample_flag_data["name"],
        sample_flag_data["environment"],
        update_data
    )
    
    assert updated_flag is not None
    assert updated_flag.enabled is False
    assert updated_flag.rollout == 50
    assert updated_flag.id == created_flag.id


def test_update_nonexistent_flag(db_session):
    """Test updating a flag that doesn't exist."""
    update_data = FeatureFlagUpdate(enabled=False)
    result = update_flag(db_session, "nonexistent", "dev", update_data)
    assert result is None


def test_delete_flag(db_session, sample_flag_data):
    """Test deleting a feature flag."""
    flag_data = FeatureFlagCreate(**sample_flag_data)
    create_flag(db_session, flag_data)
    
    # Delete the flag
    success = delete_flag(db_session, sample_flag_data["name"], sample_flag_data["environment"])
    assert success is True
    
    # Verify it's deleted
    flag = get_flag(db_session, sample_flag_data["name"], sample_flag_data["environment"])
    assert flag is None


def test_delete_nonexistent_flag(db_session):
    """Test deleting a flag that doesn't exist."""
    success = delete_flag(db_session, "nonexistent", "dev")
    assert success is False

