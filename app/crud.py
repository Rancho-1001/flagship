from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from app.models import FeatureFlag
from app.schemas import FeatureFlagCreate, FeatureFlagUpdate
from app.exceptions import FlagAlreadyExistsError, DatabaseError
from app.logger import logger


def get_flag(db: Session, name: str, environment: str) -> Optional[FeatureFlag]:
    """Get a feature flag by name and environment."""
    logger.debug(f"Getting flag: name={name}, environment={environment}")
    flag = db.query(FeatureFlag).filter(
        FeatureFlag.name == name,
        FeatureFlag.environment == environment
    ).first()
    
    if flag:
        logger.info(f"Flag found: {name} in {environment}")
    else:
        logger.debug(f"Flag not found: {name} in {environment}")
    
    return flag


def get_flag_by_id(db: Session, flag_id: str) -> Optional[FeatureFlag]:
    """Get a feature flag by ID."""
    return db.query(FeatureFlag).filter(FeatureFlag.id == flag_id).first()


def list_flags(
    db: Session, 
    environment: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[FeatureFlag]:
    """List all feature flags, optionally filtered by environment."""
    logger.debug(f"Listing flags: environment={environment}, skip={skip}, limit={limit}")
    query = db.query(FeatureFlag)
    
    if environment:
        query = query.filter(FeatureFlag.environment == environment)
    
    flags = query.offset(skip).limit(limit).all()
    logger.info(f"Retrieved {len(flags)} flag(s)")
    return flags


def count_flags(db: Session, environment: Optional[str] = None) -> int:
    """Count feature flags, optionally filtered by environment."""
    query = db.query(FeatureFlag)
    
    if environment:
        query = query.filter(FeatureFlag.environment == environment)
    
    return query.count()


def create_flag(db: Session, flag_data: FeatureFlagCreate) -> FeatureFlag:
    """Create a new feature flag."""
    logger.info(f"Creating flag: name={flag_data.name}, environment={flag_data.environment}")
    
    # Check if flag already exists
    existing = get_flag(db, flag_data.name, flag_data.environment)
    if existing:
        logger.warning(f"Attempted to create duplicate flag: {flag_data.name} in {flag_data.environment}")
        raise FlagAlreadyExistsError(flag_data.name, flag_data.environment)
    
    flag = FeatureFlag(
        name=flag_data.name,
        environment=flag_data.environment,
        enabled=flag_data.enabled,
        rollout=flag_data.rollout
    )
    
    try:
        db.add(flag)
        db.commit()
        db.refresh(flag)
        logger.info(f"Successfully created flag: {flag_data.name} in {flag_data.environment} (id={flag.id})")
        return flag
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error creating flag: {e}")
        raise FlagAlreadyExistsError(flag_data.name, flag_data.environment)
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating flag: {e}", exc_info=True)
        raise DatabaseError(f"Failed to create feature flag: {str(e)}")


def update_flag(
    db: Session, 
    name: str, 
    environment: str, 
    flag_data: FeatureFlagUpdate
) -> Optional[FeatureFlag]:
    """Update an existing feature flag."""
    logger.info(f"Updating flag: name={name}, environment={environment}")
    
    flag = get_flag(db, name, environment)
    if not flag:
        logger.warning(f"Attempted to update non-existent flag: {name} in {environment}")
        return None
    
    # Track changes
    changes = []
    if flag_data.enabled is not None and flag_data.enabled != flag.enabled:
        changes.append(f"enabled: {flag.enabled} -> {flag_data.enabled}")
        flag.enabled = flag_data.enabled
    if flag_data.rollout is not None and flag_data.rollout != flag.rollout:
        changes.append(f"rollout: {flag.rollout} -> {flag_data.rollout}")
        flag.rollout = flag_data.rollout
    
    if not changes:
        logger.debug(f"No changes to apply for flag: {name} in {environment}")
        return flag
    
    try:
        db.commit()
        db.refresh(flag)
        logger.info(f"Successfully updated flag: {name} in {environment} - Changes: {', '.join(changes)}")
        return flag
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error updating flag: {e}")
        raise DatabaseError("Failed to update feature flag due to database constraint violation")
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error updating flag: {e}", exc_info=True)
        raise DatabaseError(f"Failed to update feature flag: {str(e)}")


def delete_flag(db: Session, name: str, environment: str) -> bool:
    """Delete a feature flag."""
    logger.info(f"Deleting flag: name={name}, environment={environment}")
    
    flag = get_flag(db, name, environment)
    if not flag:
        logger.warning(f"Attempted to delete non-existent flag: {name} in {environment}")
        return False
    
    try:
        db.delete(flag)
        db.commit()
        logger.info(f"Successfully deleted flag: {name} in {environment} (id={flag.id})")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting flag: {e}", exc_info=True)
        raise DatabaseError(f"Failed to delete feature flag: {str(e)}")
