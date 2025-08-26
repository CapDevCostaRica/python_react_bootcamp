# D&D 5e Forward Proxy Caching Service

This service provides a forward proxy with caching for the D&D 5e API, implementing GET endpoints with query parameters.

## Features

- **Forward Proxy Caching**: Caches D&D monsters data locally to reduce API calls
- **GET Endpoints**: Simple GET requests with query parameters
- **Input/Output Validation**: Marshmallow schemas for request and response validation
- **Database Integration**: PostgreSQL for local data storage

## Endpoints

### 1. List Monsters (`GET /list`)

Lists all available monsters with caching.

**Request:**
```
GET /list
```

**Response:**
```json
{
  "count": 334,
  "results": [
    {
      "index": "aboleth",
      "name": "Aboleth",
      "url": "/api/monsters/aboleth"
    },
    ...
  ]
}
```

**cURL Example:**
```bash
curl "http://localhost:4000/list"
```

### 2. Get Monster (`GET /get/<index>`)

Retrieves a specific monster by index with caching.

**Request:**
```
GET /get/aboleth
```

**Response:**
```json
{
  "index": "aboleth",
  "name": "Aboleth",
  "size": "Large",
  "type": "aberration",
  "alignment": "lawful evil",
  "armor_class": [
    {
      "type": "natural",
      "value": 17
    }
  ],
  "hit_points": 135,
  "hit_dice": "18d12",
  "challenge_rating": 10,
  "proficiency_bonus": 4,
  "xp": 5900,
  ...
}
```

**cURL Example:**
```bash
curl "http://localhost:4000/get/aboleth"
```

### 3. Health Check (`GET /health`)

Service health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "service": "dnd-proxy"
}
```

## Caching Behavior

- **First Request**: Data is fetched from the upstream D&D 5e API and cached in the local database
- **Subsequent Requests**: Data is served from the local cache for improved performance
- **List Endpoint**: Caches basic monster information (index, name, url)
- **Get Endpoint**: Caches complete monster details when first requested

## Error Handling

The service provides comprehensive error handling with appropriate HTTP status codes:

- `400 Bad Request`: Invalid request data or validation errors
- `404 Not Found`: Monster not found in upstream API
- `500 Internal Server Error`: Database or internal errors
- `502 Bad Gateway`: Upstream API unavailable

## Database Schema

The service uses a `monsters` table with the following structure:

- **Basic Info**: index (unique), name, size, type, alignment
- **Stats**: armor_class, hit_points, ability scores (STR, DEX, CON, INT, WIS, CHA)
- **Combat**: actions, legendary_actions, reactions, special_abilities
- **Other**: JSON fields for complex data structures (proficiencies, immunities, etc.)

## Setup and Deployment

1. Ensure PostgreSQL is running
2. Run database migrations: `alembic upgrade head`
3. Install dependencies: `pip install -r requirements.txt`
4. Start the service: `python main.py`

The service runs on port 4000 by default.
