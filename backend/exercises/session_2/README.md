# Stories

As a user, I want a seeder script to read the different files in the exercise to seed my database at startup.
As a user, I want an endpoint that allows me to provide different characteristics and retrieve the matching people.

# Technical notes

Import the CSV files, including those under the files directory. Ensure that you do not duplicate the seeding, follow the correct hierarchy in your ETL, and use the more memory-efficient approach. 

Create an endpoint (/people/find) that a user can call to retrieve people records, and return the result count and a list of names.

Example:

{
    "result": true, 
    "data": {
        "total": 3,
        "results": ["Misty Greene", "Jason Riley", "Harold Pierce"]
    }
}

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
People with average weight above 70 grouped by hair color
Most common food overall
Average weight grouped by nationality and hair color using ROLLUP to include subtotals.
The top 2 oldest people per nationality
People ranked by how many hobbies they have
Average height by nationality and average in general