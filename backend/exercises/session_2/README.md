# Stories

As a user I want a seeder script to read the different files in the exercise to seed my database at start up
As a user I want an endpoint I can give differnet characteristics and get the matching people

# Technical nots

Import the CSV files including under files directory, make sure you do not duplicate the seeding, make sure you follow the right herarchy on your ETL, use the more memory efficient approach. 

Create an endpoit a user can call to find people, and return the result count and a list of their name in a single string

-Add endpoint route

Example:

{
    "result": true, 
    "data": {
        "total": 3,
        "results": ["Misty Greene", "Jason Riley", "Harold Pierce"]
    }
}

Include tests for the following people

### Test 1
I have hazel eyes and black hair, hold a PhD, enjoy dancing, love lasagna, and I am a mother.

### Test 2
I have green eyes and black hair, earned a Certificate, enjoy playing chess, like to eat salad, and I am an aunt.

### Test 3
I have blue eyes and brown hair, and I’m from Mexico.

### Test 4
I have hazel eyes and black hair, I’m 39 years old, and I’m Spanish.

### Test 5
I have green eyes and brown hair, and I’m 25 years old.

# For extra points

Create and endpoint for each one of this reports, return the same format as the previous exercise

People who like both sushi and ramen
People with average weight above 70 grouped by hair color
Most common food overall
Average weight grouped by nationality and hair color using ROLLUP to include subtotals
Top 2 oldest people per nationality
People ranked by how many hobbies they have
Average height by nationality and total