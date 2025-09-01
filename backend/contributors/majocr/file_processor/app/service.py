from app.models import Family_majocr, Food_majocr, Hobby_majocr, People_majocr, Person_Food_Association_majocr, Person_Hobby_Association_majocr, Study_majocr

def query_people_by_filters(session, filters):
    print(f"Querying with filters.")
    query = session.query(People_majocr).distinct()

    query = query.join(People_majocr.foods).join(Person_Food_Association_majocr.food)
    query = query.join(People_majocr.hobbies).join(Person_Hobby_Association_majocr.hobby)
    query = query.join(People_majocr.family)
    query = query.join(People_majocr.studies)

    if 'eye_color' in filters:
        query = query.filter(People_majocr.eye_color == filters['eye_color'])
    if 'hair_color' in filters:
        query = query.filter(People_majocr.hair_color == filters['hair_color'])
    if 'age' in filters:
        query = query.filter(People_majocr.age == filters['age'])
    if 'height_cm' in filters:
        query = query.filter(People_majocr.height_cm == filters['height_cm'])
    if 'weight_kg' in filters:
        query = query.filter(People_majocr.weight_kg == filters['weight_kg'])
    if 'nationality' in filters:
        query = query.filter(People_majocr.nationality == filters['nationality'])

    if 'food' in filters:
        query = query.filter(Food_majocr.name.ilike(filters['food']))
    if 'hobby' in filters:
        query = query.filter(Hobby_majocr.name.ilike(filters['hobby']))
    if 'family' in filters:
        query = query.filter(Family_majocr.relation.ilike(filters['family']))
    if 'degree' in filters:
        query = query.filter(Study_majocr.degree.ilike(filters['degree']))
    if 'institution' in filters:
        query = query.filter(Study_majocr.institution.ilike(filters['institution']))

    return query.all()
