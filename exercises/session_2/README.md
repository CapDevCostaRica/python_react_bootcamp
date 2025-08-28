# Stories

As a user, I want a seeder script to read the different files in the exercise to seed my database at startup.

As a user, I want an endpoint that allows me to provide different characteristics and retrieve the matching people.

# Technical notes

Please reset your database 

```shell
docker-compose run flask_app bash /app/run_local.sh reset_db
```

Copy backend/contributors/capdevcr/boilerplate to backend/contributors/your_username/your_app_name.

Follow the main README file instructions about creating migrations.

Import the CSV files, including those under the files directory, use backend/contributors/your_username/your_app_name/seeds.py to do this procedure. Ensure that you do not duplicate the seeding, follow the correct hierarchy in your ETL, and use the more memory-efficient approach. 

Create an endpoint GET(/people/find) that a user can call to retrieve people records, and return the result count and a list of names.

Query example:

```json
{
    "filters" : {
      "food": "lasagna",
      "family": "mother",  
      "hobby": "gaming",
      "eye_color": "hazel",
      "hair_color": "black",
      "age": 25,
      "height_cm": 165,
      "weight_kg": 65,
      "nationality": "German",
      "degree": "PhD",
      "institution": "MIT"
    }
}
```

Note: not all filters are required

Response example:

```json
{
    "success": true, 
    "data": {
        "total": 3,
        "results": ["Misty Greene", "Jason Riley", "Harold Pierce"]
    }
}
```

Include tests for the following people.

### Test 1
I have hazel eyes and black hair, hold a PhD, enjoy dancing, love lasagna, and am a mother.

### Test 2
I have green eyes and black hair, hold a Certificate, enjoy playing chess, like eating salad, and I am an aunt.

### Test 3
I have blue eyes and brown hair, and I'm from Mexico.

### Test 4
I have hazel eyes and black hair; I'm 39 years old, and I'm from Spain.

### Test 5
I have green eyes and brown hair, and I'm 25 years old.

# For extra points

Create an endpoint for each one of these reports, and return the same format as the previous exercise.

People who like both sushi and ramen
Route: /people/sushi_ramen
Example response

```json
{
    "success": true, 
    "data": 3
}
```

People with average weight above 70 grouped by hair color
Route: /people/avg_weight_above_70_hair
Example response

```json
{
    "success": true, 
    "data": {
        "hazel" : 85,
        "black" : 98
    }
}
```

Most common food overall
Route: /people/most_common_food_overall
Example response

```json
{ 
    "success": true, 
    "data": "pizza" 
}
```

Average weight grouped by nationality and hair color
Route: /people/avg_weight_nationality_hair
Example response

```json
{
    "success": true, 
    "data": {
        "mexican-hazel" : 45,
        "spanish-black" : 98
    }
}
```

The top 2 oldest people per nationality
Route: /people/top_oldest_nationality
Example response

```json
{
    "success": true, 
    "data": {
        "mexican" : ["Michael Callahan", "Stephen Thompson"],
        "spanish" : ["Amy James", "Dominique Medina"]
    }
}
```

People ranked by how many hobbies they have (Top 3)
Route: /people/top_hobbies
Example response

```json
{
    "success": true, 
    "data": ["Michael Callahan", "Stephen Thompson", "Tammy Arnold"]
}
```

Average height by nationality and average in general
Route: /people/avg_height_nationality_general
Example response

```json
{
    "success": true, 
    "data": {
        "general": 56,
        "nationalities": {
            "spanish": 78,
            "mexican": 98,
            "american": 0
        }
    }
}
