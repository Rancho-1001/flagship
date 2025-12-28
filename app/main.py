from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
import time
from app.database import SessionLocal, engine, Base
from app.models import FeatureFlag
from app.crud import (
    get_flag,
    list_flags,
    count_flags,
    create_flag,
    update_flag,
    delete_flag
)
from app.schemas import (
    FeatureFlagCreate,
    FeatureFlagUpdate,
    FeatureFlagResponse,
    FeatureFlagListResponse
)
from app.exceptions import (
    FlagNotFoundError,
    FlagAlreadyExistsError,
    InvalidInputError,
    DatabaseError
)
from app.logger import logger
from app.auth import verify_api_key

# Note: Database tables are created via Alembic migrations
# Run: alembic upgrade head
# Base.metadata.create_all(bind=engine)  # Only for development, use Alembic in production

app = FastAPI(
    title="FlagShip",
    description="Feature flag management service built with FastAPI and PostgreSQL",
    version="1.0.0"
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests and responses."""
    start_time = time.time()
    
    # Log request
    logger.info(
        f"Request: {request.method} {request.url.path} - "
        f"Client: {request.client.host if request.client else 'unknown'}"
    )
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Response: {request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.3f}s"
        )
        
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Error processing {request.method} {request.url.path} - "
            f"Time: {process_time:.3f}s - Error: {str(e)}",
            exc_info=True
        )
        raise


# Exception handlers
@app.exception_handler(FlagNotFoundError)
@app.exception_handler(FlagAlreadyExistsError)
@app.exception_handler(InvalidInputError)
@app.exception_handler(DatabaseError)
async def flagship_exception_handler(request: Request, exc: HTTPException):
    """Handle custom FlagShip exceptions."""
    logger.warning(f"FlagShip exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status_code": 500}
    )


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint with database connectivity check."""
    try:
        # Test database connection
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db_status = "connected"
        logger.debug("Health check: Database connection successful")
    except Exception as e:
        db_status = "disconnected"
        logger.error(f"Health check: Database connection failed - {e}")
    
    status = "healthy" if db_status == "connected" else "degraded"
    
    return {
        "status": status,
        "service": "FlagShip",
        "database": db_status
    }


@app.post("/flags", response_model=FeatureFlagResponse, status_code=201)
def create_feature_flag(
    flag_data: FeatureFlagCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Create a new feature flag."""
    try:
        flag = create_flag(db, flag_data)
        return flag
    except (FlagAlreadyExistsError, InvalidInputError, DatabaseError):
        # These are already HTTPExceptions, just re-raise
        raise
    except Exception as e:
        logger.error(f"Unexpected error in create_feature_flag: {e}", exc_info=True)
        raise DatabaseError(f"Failed to create feature flag: {str(e)}")


@app.get("/flags", response_model=FeatureFlagListResponse)
def list_feature_flags(
    environment: Optional[str] = Query(None, description="Filter by environment"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """List all feature flags, optionally filtered by environment."""
    flags = list_flags(db, environment=environment, skip=skip, limit=limit)
    total = count_flags(db, environment=environment)
    
    return FeatureFlagListResponse(flags=flags, total=total)


@app.get("/flags/{name}", response_model=FeatureFlagResponse)
def fetch_feature_flag(
    name: str,
    environment: str = Query(..., description="Environment (dev, staging, prod)"),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get a specific feature flag by name and environment."""
    flag = get_flag(db, name, environment)
    if not flag:
        raise FlagNotFoundError(name, environment)
    return flag


@app.put("/flags/{name}", response_model=FeatureFlagResponse)
def update_feature_flag(
    name: str,
    environment: str = Query(..., description="Environment (dev, staging, prod)"),
    flag_data: FeatureFlagUpdate = ...,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Update an existing feature flag."""
    try:
        flag = update_flag(db, name, environment, flag_data)
        if not flag:
            raise FlagNotFoundError(name, environment)
        return flag
    except (FlagNotFoundError, InvalidInputError, DatabaseError):
        # These are already HTTPExceptions, just re-raise
        raise
    except Exception as e:
        logger.error(f"Unexpected error in update_feature_flag: {e}", exc_info=True)
        raise DatabaseError(f"Failed to update feature flag: {str(e)}")


@app.delete("/flags/{name}", status_code=204)
def delete_feature_flag(
    name: str,
    environment: str = Query(..., description="Environment (dev, staging, prod)"),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Delete a feature flag."""
    try:
        success = delete_flag(db, name, environment)
        if not success:
            raise FlagNotFoundError(name, environment)
        return None
    except (FlagNotFoundError, DatabaseError):
        # These are already HTTPExceptions, just re-raise
        raise
    except Exception as e:
        logger.error(f"Unexpected error in delete_feature_flag: {e}", exc_info=True)
        raise DatabaseError(f"Failed to delete feature flag: {str(e)}")
