# D&D Forward Proxy Caching Service

## Overview
This service provides a forward proxy caching API for Dungeons & Dragons monsters.
It caches responses from the upstream D&D 5e API (https://www.dnd5eapi.co/api/) in a local PostgreSQL database, reducing latency and external API calls.


## Features
- **POST /list:** List all monsters (payload: `{ "resource": "monsters" }`)
- **POST /get:** Get a specific monster by index (payload: `{ "monster_index": "<index>" }`)
- Caches both the monster list and individual monster data in the local database
- Input and output validation using Marshmallow schemas
- Modular architecture with separation of concerns:
  - **main.py**: App initialization and configuration
  - **endpoints.py**: API route handlers and Flask-RESTful resources
  - **schemas.py**: Input/output validation schemas
  - **service.py**: Business logic for caching and proxy functionality
- Integration tests for all endpoints

## Folder Structure
```
backend/contributors/randymorales/dnd/
    main.py              # Flask app setup and endpoint registration
    endpoints.py         # API endpoint classes and route handlers
    schemas.py           # Marshmallow validation schemas
    service.py           # Proxy caching service logic
    requirements.txt     # Python dependencies
    test_integration.py  # Integration tests for API endpoints
```

## Prerequisites
- **Python 3.8+** (recommended: use a virtual environment)
- **Docker & Docker Compose** (for running PostgreSQL and the Flask app)
- **PostgreSQL** (if running locally, e.g. for migrations)
  - On macOS: `brew install postgresql`
- **Alembic** (for database migrations)

## Setup & Installation

### 1. Clone the repository and checkout the correct branch

```bash
git clone <repo-url>
cd python_react_bootcamp
git checkout randymorales_forward_proxy_caching
```

### 2. Install Python dependencies

It is recommended to use a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
cd backend/contributors/randymorales/dnd
pip install -r requirements.txt
cd ../../../../
```

### 3. Start the services with Docker Compose

This will start both the Flask app and a PostgreSQL database:

```bash
docker-compose up -d
```

### 4. Run database migrations

This creates the necessary tables for caching:

```bash
PYTHONPATH=backend/framework .venv/bin/alembic -c backend/framework/alembic.ini upgrade head
```

### 5. Restart the Flask app (if needed)

```bash
docker-compose restart flask_app
```

## Usage

### List all monsters

```bash
curl -X POST http://localhost:4000/list -H 'Content-Type: application/json' -d '{"resource": "monsters"}'
```

### Get a specific monster

```bash
curl -X POST http://localhost:4000/get -H 'Content-Type: application/json' -d '{"monster_index": "bat"}'
```

## Testing

### Run Integration Tests

The service includes comprehensive integration tests that verify all endpoints and functionality:

```bash
# Run tests inside the Docker container
docker compose exec flask_app pytest /app/contributors/randymorales/dnd/test_integration.py --maxfail=3 --disable-warnings -q

# Or run tests locally (requires proper environment setup)
cd backend/contributors/randymorales/dnd
python -m pytest test_integration.py -v
```

### Manual Testing Examples

```bash
# Test the list endpoint
curl -X POST http://localhost:4000/list -H 'Content-Type: application/json' -d '{"resource": "monsters"}' | python3 -m json.tool

# Test the get endpoint with a specific monster
curl -X POST http://localhost:4000/get -H 'Content-Type: application/json' -d '{"monster_index": "aboleth"}' | python3 -m json.tool
```

## Configuration

- Environment variables for the database are set in `.env` and used by Docker Compose.
- The Flask app and DB are both containerized for easy local development.

## Findings & Notes

- **PostgreSQL must be installed** on your system if you want to run migrations or connect locally outside Docker. Install with `brew install postgresql` on macOS.
- **Database migrations** are managed with Alembic. If you add new models, create a new migration in `backend/framework/alembic/versions/`.
- **Caching**: The service first checks the local DB for data. If not found, it fetches from the upstream API and caches the result.
- **Validation**: All input and output is validated with Marshmallow schemas for reliability.
- **Modular Design**: The codebase follows separation of concerns principles:
  - API routes are separated from business logic
  - Validation schemas are centralized in one module
  - Service logic is independent and testable
  - Main app file only handles configuration and routing setup

## Troubleshooting
- If you get DB connection errors, ensure Docker Compose is running and the `flask_db` service is healthy.
- If you change models, always re-run migrations and restart the Flask app.
- For local DB access, ensure PostgreSQL is running and accessible on the expected port (default: 5432).
- **Import errors**: The modular structure requires proper Python path setup. The service automatically handles this in `service.py`.
- **Module not found errors**: Ensure you're running commands from the correct directory and the Python environment is properly configured.

## Authors
- @randymorales (feature implementation)

