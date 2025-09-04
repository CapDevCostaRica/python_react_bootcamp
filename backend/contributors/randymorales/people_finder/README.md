# People Finder API

A Flask API for finding people based on multiple criteria including physical characteristics, family relationships, hobbies, favorite foods, and educational background.

## API Endpoints

### Core Endpoints

#### `GET /`

Health check endpoint.

**Response:**
```json
{"status": "ok"}
```

#### `GET /people/find`

Find people based on multiple filter criteria.

**Request Format:**
Query parameters using `filters[key]=value` format:
```
GET /people/find?filters[eye_color]=hazel&filters[hair_color]=black&filters[age]=39
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total": 1,
    "results": ["Regina Fisher"]
  }
}
```

### Extra Credit Endpoints

#### `GET /people/sushi_ramen`

Find people who like both sushi and ramen.

**Response:**
```json
{
  "success": true,
  "data": 0
}
```

#### `GET /people/avg_weight_above_70_hair`

Get people with average weight above 70 grouped by hair color.

**Response:**
```json
{
  "success": true,
  "data": {
    "auburn": 74,
    "black": 78,
    "brown": 78,
    "gray": 77,
    "red": 70
  }
}
```

#### `GET /people/most_common_food_overall`

Get the most common food overall.

**Response:**
```json
{
  "success": true,
  "data": "curry"
}
```

#### `GET /people/avg_weight_nationality_hair`

Get average weight grouped by nationality and hair color.

**Response:**
```json
{
  "success": true,
  "data": {
    "mexican-black": 75,
    "spanish-brown": 82,
    "american-blonde": 68,
    "brazilian-auburn": 70,
    "canadian-gray": 74,
    "french-red": 80
  }
}
```

#### `GET /people/top_oldest_nationality`

Get the top 2 oldest people per nationality.

**Response:**
```json
{
  "success": true,
  "data": {
    "mexican": ["Paul Kelly", "Kimberly Mayer"],
    "spanish": ["William Hurley", "Richard Howard"],
    "american": ["Andre Newman", "Samantha Mathis"],
    "brazilian": ["Robert Leonard", "Emily Martinez"],
    "canadian": ["Stephen Thompson", "Zachary Diaz"],
    "french": ["Nicholas Perez", "Lisa Miller"],
    "german": ["Alexander Jensen", "Yvonne Marshall"],
    "nigerian": ["Logan Lee", "Jack Owens MD"]
  }
}
```

#### `GET /people/top_hobbies`

Get people ranked by how many hobbies they have (Top 3).

**Response:**
```json
{
  "success": true,
  "data": ["Tony Hoffman", "Calvin Gallegos", "Christopher Hall"]
}
```

#### `GET /people/avg_height_nationality_general`

Get average height by nationality and general average.

**Response:**
```json
{
  "success": true,
  "data": {
    "general": 176,
    "nationalities": {
      "spanish": 183,
      "american": 180,
      "german": 179,
      "mexican": 178,
      "brazilian": 176,
      "canadian": 175,
      "french": 174,
      "nigerian": 169
    }
  }
}
```

## Available Filters

- **Physical:** `eye_color`, `hair_color`, `age`, `height_cm`, `weight_kg`, `nationality`
- **Family:** `family` (relation type: mother, father, sister, etc.)
- **Food:** `food` (favorite food)
- **Hobbies:** `hobby` (hobby name)
- **Education:** `degree`, `institution`

## Project Structure

```
people_finder/
├── main.py              # Main Flask application (minimal, endpoints only)
├── seeds.py             # Database seeding script
├── requirements.txt     # Python dependencies
├── alembic.ini          # Alembic configuration
├── data/                # Local CSV data files
│   ├── people_data.csv
│   ├── physical_data.csv
│   ├── family_data.csv
│   ├── favorite_data.csv
│   ├── hobbies_data.csv
│   └── studies_data.csv
├── app/
│   ├── models.py        # Database models (with randymorales prefix)
│   ├── database.py      # Database configuration and session management
│   └── services.py      # Business logic for people finder
├── alembic/
│   └── versions/        # Database migration files
├── test_integration.py  # Integration tests for core functionality
└── test_extra_credit.py # Integration tests for extra credit endpoints
```

## Setup and Usage

### Prerequisites

- Docker and Docker Compose
- The application is designed to run within the python_react_bootcamp framework

### Running the Application

1. Start the application:
```bash
cd ~/capdevcr/python_react_bootcamp
APPLICATION_FOLDER=randymorales/people_finder docker-compose up -d
```

2. The API will be available at `http://localhost:4000`

### Database Setup

The application automatically:
1. Runs database migrations on startup
2. Seeds the database with CSV data from the `data/` directory
3. Prevents duplicate seeding on subsequent runs

### Testing

Run the integration tests:
```bash
docker-compose exec flask_app bash -c "cd /app/contributors/randymorales/people_finder && python test_integration.py"
```

Run the extra credit endpoint tests:
```bash
docker-compose exec flask_app bash -c "cd /app/contributors/randymorales/people_finder && python test_extra_credit.py"
```

## Features

### Database Models
All models are prefixed with `randymorales` to avoid conflicts:
- `RandymoralesPerson` - Basic person information
- `RandymoralesPhysicalData` - Physical characteristics
- `RandymoralesFamilyRelation` - Family relationships
- `RandymoralesFavoriteFood` - Food preferences
- `RandymoralesHobby` - Hobbies and interests
- `RandymoralesStudy` - Educational background

### Core Functionality
- **People Finder**: Advanced filtering system supporting multiple criteria
- **Data Seeding**: Automated CSV import with batch processing
- **Database Management**: Clean migrations with prefixed tables

### Extra Credit Features
- **Analytics Endpoints**: 7 additional endpoints providing statistical insights
- **Complex Queries**: Multi-table joins, aggregations, and ranking
- **Performance Optimized**: Efficient queries using SQLAlchemy ORM

## Architecture

### Separation of Concerns
- **main.py:** Minimal Flask app with endpoint definitions
- **services.py:** Business logic and database query logic
- **database.py:** Database configuration and session management
- **models.py:** SQLAlchemy model definitions

### Data Management
- CSV files are stored locally in the `data/` directory
- Database uses prefixed table names to avoid conflicts
- Efficient batch processing for data seeding
- Memory-efficient query patterns with proper session management

## Performance Features

- Efficient database queries using joins and subqueries
- Batch processing for data import
- Proper database session management
- Indexed foreign key relationships
- Optimized query patterns for complex filters

## Database Schema

The database schema includes proper relationships:
- People as the main entity
- One-to-one relationship with physical data
- One-to-many relationships with family, foods, hobbies, and studies
- Foreign key constraints ensure data integrity
