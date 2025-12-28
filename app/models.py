from sqlalchemy import Column, String, Boolean, Integer, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from datetime import datetime
import uuid
from app.database import Base


class FeatureFlag(Base):
    __tablename__ = "feature_flags"
    
    # Unique constraint on name + environment combination
    __table_args__ = (
        UniqueConstraint('name', 'environment', name='uq_flag_name_environment'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, index=True)
    environment = Column(String(50), nullable=False, index=True)
    enabled = Column(Boolean, default=False, nullable=False)
    rollout = Column(Integer, default=100, nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
