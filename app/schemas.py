from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from uuid import UUID


class FeatureFlagBase(BaseModel):
    """Base schema for feature flag with common fields."""
    name: str = Field(..., min_length=1, max_length=100, description="Feature flag name/key")
    environment: str = Field(..., min_length=1, max_length=50, description="Environment (dev, staging, prod)")
    enabled: bool = Field(default=False, description="Whether the flag is enabled")
    rollout: int = Field(default=100, ge=0, le=100, description="Rollout percentage (0-100)")
    
    @validator('environment')
    def validate_environment(cls, v):
        """Validate environment value."""
        allowed = ['dev', 'staging', 'prod', 'development', 'production']
        if v.lower() not in allowed:
            raise ValueError(f"Environment must be one of: {', '.join(allowed)}")
        return v.lower()


class FeatureFlagCreate(FeatureFlagBase):
    """Schema for creating a new feature flag."""
    pass


class FeatureFlagUpdate(BaseModel):
    """Schema for updating a feature flag (all fields optional)."""
    enabled: Optional[bool] = Field(None, description="Whether the flag is enabled")
    rollout: Optional[int] = Field(None, ge=0, le=100, description="Rollout percentage (0-100)")
    
    @validator('rollout')
    def validate_rollout(cls, v):
        """Validate rollout percentage."""
        if v is not None and (v < 0 or v > 100):
            raise ValueError("Rollout must be between 0 and 100")
        return v


class FeatureFlagResponse(FeatureFlagBase):
    """Schema for feature flag response."""
    id: UUID
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FeatureFlagListResponse(BaseModel):
    """Schema for list of feature flags."""
    flags: list[FeatureFlagResponse]
    total: int
