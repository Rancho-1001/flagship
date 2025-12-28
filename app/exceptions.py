"""
Custom exceptions for FlagShip API.
Provides specific exception types for better error handling.
"""
from fastapi import HTTPException, status


class FlagShipException(HTTPException):
    """Base exception for FlagShip API."""
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class FlagNotFoundError(FlagShipException):
    """Raised when a feature flag is not found."""
    def __init__(self, name: str, environment: str):
        detail = f"Feature flag '{name}' not found in environment '{environment}'"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class FlagAlreadyExistsError(FlagShipException):
    """Raised when trying to create a flag that already exists."""
    def __init__(self, name: str, environment: str):
        detail = f"Feature flag '{name}' already exists in environment '{environment}'"
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class InvalidInputError(FlagShipException):
    """Raised when input validation fails."""
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class DatabaseError(FlagShipException):
    """Raised when a database operation fails."""
    def __init__(self, detail: str = "Database operation failed"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

