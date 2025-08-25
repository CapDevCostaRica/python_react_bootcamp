# DnD API

## Overview

This project is an API for accessing Dungeons and Dragons monster information. It provides endpoints to:

1. List all available monsters
2. Get detailed information about a specific monster

The API first checks if the requested data is available in the database. If not, it fetches the data from an external DnD API, stores it in the database, and returns it to the client.

## Application Structure

- `main.py` - Entry point of the application
- `app/` - Contains the application code
  - `controllers/` - API route handlers
  - `services/` - Business logic for fetching and processing monster data
  - `models/` - Database models
  - `schemas/` - Request and response validation schemas
- `tests/` - Contains test files

## Running the API

To run the API endpoint, follow these steps:

1. Ensure you have Python 3.x installed
2. Install required dependencies:
  ```
  pip install -r requirements.txt
  ```
3. Start the server:
  ```
  python main.py
  ```
  
The API will be available at `http://localhost:4000` (or your configured port).

## Available Endpoints

- `POST /monsters/list` - Get all monsters
  - Request body: `{"resource": "monsters"}`
  - Response: List of all monsters with count and results

- `POST /monsters/get` - Get a specific monster by index
  - Request body: `{"monster_index": "monster-index-name"}`
  - Response: Detailed information about the requested monster

## Running Tests

This project uses pytest for testing. To run the tests:

In folder /backend/contributors/kevinWalshMunoz/dnd/tests, execute the following command:

```bash
pytest test_monster_api.py -v
```

The `-v` flag enables verbose output, showing more details about each test being run.

## Test Coverage

The tests verify:
- Getting the list of monsters from the database
- Getting monsters from external API when the database is empty
- Getting a specific monster by index from the database
- Getting a specific monster from external API when not found in database
- Error handling for invalid requests, including:
  - Invalid JSON
  - Missing parameters
  - Invalid parameter types
  - Empty parameters