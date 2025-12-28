# FlagShip — Build Guide

FlagShip is a lightweight backend **feature flag management service** built with FastAPI and PostgreSQL.  
It enables teams to dynamically enable, disable, and gradually roll out features **without redeploying applications**.

---

## Architecture Overview

**Request Flow**

Client → FastAPI → PostgreSQL → Response

- Clients query feature flags at runtime.
- Flags are persisted in PostgreSQL for durability and auditability.
- Configuration changes take effect immediately without redeployment.

---

## Project Structure

flagship/
├── app/
│ ├── main.py # FastAPI app and routes
│ ├── models.py # SQLAlchemy models
│ ├── schemas.py # Pydantic request/response models
│ ├── database.py # Database connection
│ ├── crud.py # Database operations
│ └── config.py # Environment configuration
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── README.md
└── BUILD.md

---


---

## Feature Flag Model

Each feature flag contains:

| Field | Description |
|-----|------------|
| id | Unique identifier (UUID) |
| name | Feature key (e.g. `new_ui`) |
| environment | Environment (`dev`, `staging`, `prod`) |
| enabled | Global on/off toggle |
| rollout | Percentage rollout (0–100) |
| updated_at | Last modification timestamp |

This model supports:
- Instant feature toggling
- Environment-specific behavior
- Gradual rollouts

---

## Step-by-Step Implementation

### 1. Dependencies

`requirements.txt`
```txt
fastapi
uvicorn
sqlalchemy
psycopg2-binary
python-dotenv

## app/database.py 

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://postgres:postgres@db:5432/flags"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


## app/models.py

from sqlalchemy import Column, String, Boolean, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.database import Base

class FeatureFlag(Base):
    __tablename__ = "feature_flags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True)
    environment = Column(String)
    enabled = Column(Boolean, default=False)
    rollout = Column(Integer, default=100)
    updated_at = Column(DateTime, default=datetime.utcnow)


## app/crud.py

from app.models import FeatureFlag

def get_flag(db, name, env):
    return db.query(FeatureFlag).filter_by(name=name, environment=env).first()

def create_flag(db, flag):
    db.add(flag)
    db.commit()
    db.refresh(flag)
    return flag

## app/main.py 

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Base, FeatureFlag
from app.crud import get_flag, create_flag

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/flags")
def create_feature_flag(name: str, env: str, enabled: bool, rollout: int, db: Session = Depends(get_db)):
    flag = FeatureFlag(name=name, environment=env, enabled=enabled, rollout=rollout)
    return create_flag(db, flag)

@app.get("/flags/{name}")
def fetch_feature_flag(name: str, env: str, db: Session = Depends(get_db)):
    flag = get_flag(db, name, env)
    if not flag:
        raise HTTPException(status_code=404, detail="Flag not found")
    return flag

## Containerization / Dockerfile 

FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

version: "3.9"

services:
  api:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: flags
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
