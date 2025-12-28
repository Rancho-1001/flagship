# FlagShip

Feature flag management service built with FastAPI and PostgreSQL.

## Quick Start

### Prerequisites
- Docker and Docker Compose installed

### Running the Service

```bash
# Start the services
docker-compose up -d

# Check logs
docker-compose logs -f api

# Test the API
curl http://localhost:8000/health
```

### API Documentation

Once running, access the interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Testing

**Unit & Integration Tests:**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

**API Testing:**
See [TESTING.md](./TESTING.md) for comprehensive testing instructions.

Quick API test:
```bash
# Run automated test script (requires API key)
python test_api.py
```

**Note**: All endpoints require API key authentication. Default key: `dev-api-key-12345`

## Features

- ✅ Full CRUD operations for feature flags
- ✅ Environment-specific flags (dev, staging, prod)
- ✅ Percentage-based rollouts
- ✅ Input validation and error handling
- ✅ RESTful API with OpenAPI documentation
- ✅ PostgreSQL persistence with Alembic migrations
- ✅ Docker containerization
- ✅ **API Key authentication** (all endpoints protected)
- ✅ **Structured logging** (request/response/error logging)
- ✅ **Comprehensive test suite** (pytest with 30+ tests)
- ✅ **Custom exception handling** (professional error responses)

## API Endpoints

**Note**: All endpoints (except `/health`) require `X-API-Key` header.

- `GET /health` - Health check (no auth required)
- `POST /flags` - Create feature flag (requires API key)
- `GET /flags` - List all flags with pagination and filtering (requires API key)
- `GET /flags/{name}` - Get specific flag (requires API key)
- `PUT /flags/{name}` - Update flag (requires API key)
- `DELETE /flags/{name}` - Delete flag (requires API key)

**Example with authentication:**
```bash
curl -H "X-API-Key: dev-api-key-12345" \
     -H "Content-Type: application/json" \
     http://localhost:8000/flags
```

## Project Structure

```
flagship/
├── app/
│   ├── main.py          # FastAPI app and routes
│   ├── models.py         # SQLAlchemy models
│   ├── schemas.py        # Pydantic request/response models
│   ├── database.py       # Database connection
│   ├── crud.py           # Database operations
│   ├── config.py         # Environment configuration
│   ├── logger.py         # Logging configuration
│   ├── exceptions.py     # Custom exceptions
│   └── auth.py           # API authentication
├── tests/
│   ├── conftest.py       # Test fixtures
│   ├── test_crud.py      # CRUD operation tests
│   ├── test_api.py       # API endpoint tests
│   └── test_auth.py      # Authentication tests
├── alembic/              # Database migrations
│   ├── env.py
│   └── versions/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── test_api.py           # Automated API test script
├── TESTING.md            # Testing guide
├── NEXT_STEPS.md         # Next steps and improvements
└── HIGH_PRIORITY_IMPLEMENTED.md  # Summary of implemented features
```

## Recent Updates ✨

**All high-priority features have been implemented!** See [HIGH_PRIORITY_IMPLEMENTED.md](./HIGH_PRIORITY_IMPLEMENTED.md) for details:

- ✅ Structured logging with request/response tracking
- ✅ Custom exception handling with proper HTTP status codes
- ✅ Comprehensive test suite (30+ tests with pytest)
- ✅ Database migrations with Alembic
- ✅ API key authentication

## Next Steps

See [NEXT_STEPS.md](./NEXT_STEPS.md) for medium-priority improvements:
- Caching (Redis)
- Rate limiting
- Monitoring & metrics
- Deployment to cloud
- And more!
