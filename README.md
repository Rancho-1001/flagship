# FlagShip 🚩

A production-ready feature flag management service built with FastAPI and PostgreSQL. Enables teams to dynamically enable, disable, and gradually roll out features without redeploying applications.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

## ✨ Features

- ✅ **Full CRUD Operations** - Create, read, update, and delete feature flags
- ✅ **Environment-Specific Flags** - Separate flags for dev, staging, and production
- ✅ **Percentage-Based Rollouts** - Gradual feature rollouts (0-100%)
- ✅ **API Key Authentication** - Secure API with key-based authentication
- ✅ **Structured Logging** - Request/response logging with error tracking
- ✅ **Comprehensive Testing** - 28 tests covering all functionality
- ✅ **Database Migrations** - Alembic for schema management
- ✅ **Docker Containerization** - Easy deployment with Docker Compose
- ✅ **Input Validation** - Pydantic schemas for request validation
- ✅ **Error Handling** - Custom exceptions with proper HTTP status codes
- ✅ **RESTful API** - OpenAPI/Swagger documentation included

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Git (for cloning)

### Running the Service

```bash
# Clone the repository
git clone https://github.com/Rancho-1001/flagship.git
cd flagship

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

## 📚 API Endpoints

**Note**: All endpoints (except `/health`) require `X-API-Key` header.

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/health` | Health check with database status | No |
| `POST` | `/flags` | Create a new feature flag | Yes |
| `GET` | `/flags` | List all flags (with pagination & filtering) | Yes |
| `GET` | `/flags/{name}?environment={env}` | Get specific flag | Yes |
| `PUT` | `/flags/{name}?environment={env}` | Update existing flag | Yes |
| `DELETE` | `/flags/{name}?environment={env}` | Delete flag | Yes |

### Example Usage

**Create a feature flag:**
```bash
curl -X POST "http://localhost:8000/flags" \
  -H "X-API-Key: dev-api-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "new_ui",
    "environment": "dev",
    "enabled": true,
    "rollout": 100
  }'
```

**List all flags:**
```bash
curl -H "X-API-Key: dev-api-key-12345" \
  "http://localhost:8000/flags"
```

**Get specific flag:**
```bash
curl -H "X-API-Key: dev-api-key-12345" \
  "http://localhost:8000/flags/new_ui?environment=dev"
```

**Update a flag:**
```bash
curl -X PUT "http://localhost:8000/flags/new_ui?environment=dev" \
  -H "X-API-Key: dev-api-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": false,
    "rollout": 50
  }'
```

**Delete a flag:**
```bash
curl -X DELETE "http://localhost:8000/flags/new_ui?environment=dev" \
  -H "X-API-Key: dev-api-key-12345"
```

## 🔐 Authentication

All API endpoints (except `/health`) require authentication via API key.

**Default API Key (Development):** `dev-api-key-12345`

**⚠️ Important:** Change the default API key in production!

Set the `API_KEYS` environment variable:
```bash
export API_KEYS="your-secure-key-1,your-secure-key-2"
```

Or in `docker-compose.yml`:
```yaml
environment:
  API_KEYS: "your-secure-key-1,your-secure-key-2"
```

## 🧪 Testing

### Running Tests

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app --cov-report=html
```

### Test Coverage

- **28 tests** covering:
  - CRUD operations (11 tests)
  - API endpoints (13 tests)
  - Authentication (4 tests)

See [TESTING.md](./TESTING.md) for comprehensive testing instructions.

## 📁 Project Structure

```
flagship/
├── app/
│   ├── main.py          # FastAPI app and routes
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic request/response models
│   ├── database.py      # Database connection
│   ├── crud.py          # Database operations
│   ├── config.py        # Environment configuration
│   ├── logger.py        # Logging configuration
│   ├── exceptions.py    # Custom exceptions
│   └── auth.py          # API authentication
├── tests/
│   ├── conftest.py      # Test fixtures
│   ├── test_crud.py     # CRUD operation tests
│   ├── test_api.py      # API endpoint tests
│   └── test_auth.py     # Authentication tests
├── alembic/             # Database migrations
│   ├── env.py
│   └── versions/
├── requirements.txt     # Python dependencies
├── Dockerfile           # Container definition
├── docker-compose.yml   # Docker Compose configuration
├── README.md            # This file
├── TESTING.md           # Testing guide
└── MIGRATION_SETUP.md   # Database migrations guide
```

## 🗄️ Database Migrations

This project uses Alembic for database migrations.

### Create a Migration

```bash
docker-compose exec api alembic revision --autogenerate -m "Description of changes"
```

### Apply Migrations

```bash
docker-compose exec api alembic upgrade head
```

### Check Migration Status

```bash
docker-compose exec api alembic current
```

See [MIGRATION_SETUP.md](./MIGRATION_SETUP.md) for detailed migration instructions.

## 🔧 Configuration

Configuration is managed via environment variables. See `app/config.py` for all available settings.

**Key Environment Variables:**
- `DATABASE_HOST` - Database hostname (default: `db`)
- `DATABASE_PORT` - Database port (default: `5432`)
- `DATABASE_USER` - Database username (default: `postgres`)
- `DATABASE_PASSWORD` - Database password (default: `postgres`)
- `DATABASE_NAME` - Database name (default: `flags`)
- `API_KEYS` - Comma-separated list of valid API keys
- `ENVIRONMENT` - Environment name (default: `development`)

## 📊 Features in Detail

### Feature Flag Model

Each feature flag contains:

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Unique identifier |
| `name` | String | Feature key (e.g., `new_ui`) |
| `environment` | String | Environment (`dev`, `staging`, `prod`) |
| `enabled` | Boolean | Global on/off toggle |
| `rollout` | Integer | Percentage rollout (0-100) |
| `updated_at` | DateTime | Last modification timestamp |

### Supported Operations

- **Instant Toggling** - Enable/disable features immediately
- **Environment Isolation** - Separate flags per environment
- **Gradual Rollouts** - Percentage-based feature releases
- **Duplicate Prevention** - Unique constraint on name + environment

## 🛠️ Development

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/Rancho-1001/flagship.git
cd flagship

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Start services
docker-compose up -d
```

### Code Quality

- **Type Hints** - Full type annotations
- **Docstrings** - Function documentation
- **Error Handling** - Custom exceptions with proper HTTP codes
- **Logging** - Structured logging throughout
- **Testing** - Comprehensive test coverage

## 🐳 Docker

### Build and Run

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down

# Stop and remove volumes (deletes database)
docker-compose down -v
```

### Services

- **api** - FastAPI application (port 8000)
- **db** - PostgreSQL database (port 5432)

## 📝 Logging

The application includes structured logging:

- **Request/Response Logging** - All HTTP requests and responses
- **Database Operations** - CRUD operation logging
- **Error Logging** - Stack traces for exceptions
- **Authentication Logging** - API key verification attempts

Logs are output to stdout and can be viewed with:
```bash
docker-compose logs -f api
```

## 🔒 Security

- **API Key Authentication** - All endpoints protected (except `/health`)
- **Input Validation** - Pydantic schemas validate all inputs
- **SQL Injection Protection** - SQLAlchemy ORM prevents SQL injection
- **Environment Variables** - Sensitive data in environment variables
- **Error Messages** - No sensitive data in error responses

## 🚀 Deployment

### Production Considerations

1. **Change Default API Key** - Set `API_KEYS` environment variable
2. **Use Strong Database Password** - Update `DATABASE_PASSWORD`
3. **Enable HTTPS** - Use reverse proxy (nginx, Traefik)
4. **Set Environment** - Set `ENVIRONMENT=production`
5. **Database Backups** - Implement regular backup strategy
6. **Monitoring** - Set up logging and monitoring
7. **Rate Limiting** - Consider adding rate limiting middleware

### Deployment Options

- **Railway** - Simple deployment with PostgreSQL
- **Render** - Easy setup with managed PostgreSQL
- **Heroku** - Classic platform with add-ons
- **AWS** - EC2, ECS, or Lambda
- **Google Cloud** - Cloud Run or App Engine
- **Azure** - App Service

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available for educational purposes.

## 👤 Author

**Rancho-1001**

- GitHub: [@Rancho-1001](https://github.com/Rancho-1001)

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- SQLAlchemy for database ORM
- Alembic for database migrations
- Pydantic for data validation

## 📚 Additional Documentation

- [TESTING.md](./TESTING.md) - Comprehensive testing guide
- [MIGRATION_SETUP.md](./MIGRATION_SETUP.md) - Database migrations guide

---

**Built with ❤️ using FastAPI and PostgreSQL**
