# FlagShip Testing Guide

This guide will help you test the FlagShip feature flag management service.

## Prerequisites

- Docker and Docker Compose installed
- `curl` command (or use the Python test script)

## Quick Start

### 1. Start the Services

```bash
# Build and start containers
docker-compose up -d

# Check logs to ensure services are running
docker-compose logs -f api
```

Wait for the API to be ready (you'll see "Application startup complete" in the logs).

### 2. Verify Services are Running

```bash
# Check container status
docker-compose ps

# Test health endpoint
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"healthy","service":"FlagShip"}
```

### 3. Access API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

You can test all endpoints directly from the Swagger UI!

## Testing Methods

### Method 1: Automated Python Test Script

Run the comprehensive test script:

```bash
# Install requests if needed
pip install requests

# Run the test script
python test_api.py
```

This script tests all endpoints and error cases automatically.

### Method 2: Manual Testing with curl

#### 1. Health Check
```bash
curl http://localhost:8000/health
```

#### 2. Create a Feature Flag
```bash
curl -X POST "http://localhost:8000/flags" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "new_ui",
    "environment": "dev",
    "enabled": true,
    "rollout": 100
  }'
```

#### 3. Get a Specific Flag
```bash
curl "http://localhost:8000/flags/new_ui?environment=dev"
```

#### 4. List All Flags
```bash
# List all flags
curl "http://localhost:8000/flags"

# List flags filtered by environment
curl "http://localhost:8000/flags?environment=dev"

# With pagination
curl "http://localhost:8000/flags?skip=0&limit=10"
```

#### 5. Update a Flag
```bash
curl -X PUT "http://localhost:8000/flags/new_ui?environment=dev" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": false,
    "rollout": 50
  }'
```

#### 6. Delete a Flag
```bash
curl -X DELETE "http://localhost:8000/flags/new_ui?environment=dev"
```

### Method 3: Using the Swagger UI

1. Open http://localhost:8000/docs in your browser
2. Click on any endpoint to expand it
3. Click "Try it out"
4. Fill in the parameters/request body
5. Click "Execute"
6. View the response

## Test Scenarios

### Scenario 1: Basic CRUD Operations

```bash
# Create
curl -X POST "http://localhost:8000/flags" \
  -H "Content-Type: application/json" \
  -d '{"name": "test_feature", "environment": "dev", "enabled": true, "rollout": 100}'

# Read
curl "http://localhost:8000/flags/test_feature?environment=dev"

# Update
curl -X PUT "http://localhost:8000/flags/test_feature?environment=dev" \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'

# Delete
curl -X DELETE "http://localhost:8000/flags/test_feature?environment=dev"
```

### Scenario 2: Multiple Environments

```bash
# Create same flag in different environments
curl -X POST "http://localhost:8000/flags" \
  -H "Content-Type: application/json" \
  -d '{"name": "new_feature", "environment": "dev", "enabled": true, "rollout": 100}'

curl -X POST "http://localhost:8000/flags" \
  -H "Content-Type: application/json" \
  -d '{"name": "new_feature", "environment": "staging", "enabled": false, "rollout": 50}'

curl -X POST "http://localhost:8000/flags" \
  -H "Content-Type: application/json" \
  -d '{"name": "new_feature", "environment": "prod", "enabled": true, "rollout": 25}'

# List all
curl "http://localhost:8000/flags"

# Filter by environment
curl "http://localhost:8000/flags?environment=prod"
```

### Scenario 3: Error Handling

```bash
# Try to create duplicate (should fail)
curl -X POST "http://localhost:8000/flags" \
  -H "Content-Type: application/json" \
  -d '{"name": "duplicate", "environment": "dev", "enabled": true, "rollout": 100}'

curl -X POST "http://localhost:8000/flags" \
  -H "Content-Type: application/json" \
  -d '{"name": "duplicate", "environment": "dev", "enabled": false, "rollout": 50}'
# Should return 400 error

# Try invalid rollout (should fail)
curl -X POST "http://localhost:8000/flags" \
  -H "Content-Type: application/json" \
  -d '{"name": "invalid", "environment": "dev", "enabled": true, "rollout": 150}'
# Should return 422 validation error

# Try to get non-existent flag (should fail)
curl "http://localhost:8000/flags/nonexistent?environment=dev"
# Should return 404 error
```

## Database Verification

You can also verify data directly in the database:

```bash
# Connect to PostgreSQL container
docker-compose exec db psql -U postgres -d flags

# Run SQL queries
SELECT * FROM feature_flags;
SELECT * FROM feature_flags WHERE environment = 'dev';
```

## Troubleshooting

### API not responding

```bash
# Check if containers are running
docker-compose ps

# Check API logs
docker-compose logs api

# Restart services
docker-compose restart
```

### Database connection issues

```bash
# Check database logs
docker-compose logs db

# Verify database is ready
docker-compose exec db pg_isready -U postgres
```

### Port already in use

If port 8000 is already in use, modify `docker-compose.yml`:

```yaml
ports:
  - "8001:8000"  # Change 8000 to 8001
```

Then access the API at http://localhost:8001

## Clean Up

```bash
# Stop and remove containers
docker-compose down

# Remove containers and volumes (deletes database data)
docker-compose down -v
```

## Performance Testing

For basic load testing, you can use `ab` (Apache Bench) or `wrk`:

```bash
# Install ab (if not available)
# macOS: brew install httpd
# Linux: sudo apt-get install apache2-utils

# Test health endpoint
ab -n 1000 -c 10 http://localhost:8000/health
```

## Next Steps

- Review the API documentation at http://localhost:8000/docs
- Integrate the API into your applications
- Set up monitoring and logging
- Configure production environment variables

