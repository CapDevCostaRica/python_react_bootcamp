from collections import defaultdict
from sqlalchemy import select, and_, func
from config import get_session
from app.models import (
    odkeyo_ex2Person as Person,
    odkeyo_ex2Physical as Physical,
    odkeyo_ex2Study as Study,
    odkeyo_ex2Family as Family,
    odkeyo_ex2FavoriteFood as FavoriteFood,
    odkeyo_ex2Hobby as Hobby,
)

def _ensure_list(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]

def build_query(filters):
    stmt = select(Person)

    need_physical = any(k in filters for k in ["eye_color","hair_color","age","height_cm","weight_kg","nationality"])
    need_studies  = any(k in filters for k in ["degree","institution"])
    need_family   = "family" in filters
    need_food     = "food" in filters
    need_hobby    = "hobby" in filters

    if need_physical:
        stmt = stmt.join(Physical, Physical.person_id == Person.id)
    if need_studies:
        stmt = stmt.join(Study, Study.person_id == Person.id)
    if need_family:
        stmt = stmt.join(Family, Family.person_id == Person.id)
    if need_food:
        stmt = stmt.join(FavoriteFood, FavoriteFood.person_id == Person.id)
    if need_hobby:
        stmt = stmt.join(Hobby, Hobby.person_id == Person.id)

    conditions = []

    def ci_in(col, values):
        vals = [v.lower() for v in values if v is not None]
        if not vals:
            return None
        return func.lower(col).in_(vals)

    if "eye_color" in filters:
        conditions.append(ci_in(Physical.eye_color, _ensure_list(filters["eye_color"])))
    if "hair_color" in filters:
        conditions.append(ci_in(Physical.hair_color, _ensure_list(filters["hair_color"])))
    if "age" in filters:
        nums = [int(v) for v in _ensure_list(filters["age"]) if str(v).isdigit()]
        if nums: conditions.append(Physical.age.in_(nums))
    if "height_cm" in filters:
        nums = [float(v) for v in _ensure_list(filters["height_cm"]) if str(v).replace(".","",1).isdigit()]
        if nums: conditions.append(Physical.height_cm.in_(nums))
    if "weight_kg" in filters:
        nums = [float(v) for v in _ensure_list(filters["weight_kg"]) if str(v).replace(".","",1).isdigit()]
        if nums: conditions.append(Physical.weight_kg.in_(nums))
    if "nationality" in filters:
        conditions.append(ci_in(Physical.nationality, _ensure_list(filters["nationality"])))

    if "degree" in filters:
        conditions.append(ci_in(Study.degree, _ensure_list(filters["degree"])))
    if "institution" in filters:
        conditions.append(ci_in(Study.institution, _ensure_list(filters["institution"])))

    if "family" in filters:
        conditions.append(ci_in(Family.relation, _ensure_list(filters["family"])))

    if "food" in filters:
        conditions.append(ci_in(FavoriteFood.food, _ensure_list(filters["food"])))

    if "hobby" in filters:
        conditions.append(ci_in(Hobby.hobby, _ensure_list(filters["hobby"])))

    conditions = [c for c in conditions if c is not None]
    if conditions:
        stmt = stmt.where(and_(*conditions))

    stmt = stmt.group_by(Person.id)
    return stmt


def report_sushi_ramen():
    with get_session() as session:
        sub = (
            select(FavoriteFood.person_id, func.count(func.distinct(func.lower(FavoriteFood.food))).label("cnt"))
            .where(func.lower(FavoriteFood.food).in_(["sushi","ramen"]))
            .group_by(FavoriteFood.person_id)
            .having(func.count(func.distinct(func.lower(FavoriteFood.food))) == 2)
        ).subquery()
        return session.execute(select(func.count()).select_from(sub)).scalar_one()

def report_avg_weight_above_70_hair():
    with get_session() as session:
        rows = session.execute(
            select(Physical.hair_color, func.avg(Physical.weight_kg))
            .where(Physical.weight_kg.isnot(None))
            .group_by(Physical.hair_color)
        ).all()
        return {hc: round(avg, 2) for hc, avg in rows if avg and avg > 70}

def report_most_common_food_overall():
    with get_session() as session:
        row = session.execute(
            select(FavoriteFood.food, func.count())
            .group_by(FavoriteFood.food)
            .order_by(func.count().desc())
            .limit(1)
        ).first()
        return row[0] if row else None

def report_avg_weight_nationality_hair():
    with get_session() as session:
        rows = session.execute(
            select(
                (func.lower(Physical.nationality) + "-" + func.lower(Physical.hair_color)).label("key"),
                func.avg(Physical.weight_kg)
            )
            .where(Physical.weight_kg.isnot(None), Physical.nationality.isnot(None), Physical.hair_color.isnot(None))
            .group_by("key")
        ).all()
        return {k: round(v, 2) for k, v in rows}

def report_top_oldest_nationality():
    with get_session() as session:
        rows = session.execute(
            select(Physical.nationality, Person.full_name, Physical.age)
            .join(Person, Person.id == Physical.person_id)
            .where(Physical.age.isnot(None), Physical.nationality.isnot(None))
            .order_by(Physical.nationality.asc(), Physical.age.desc())
        ).all()
        result = defaultdict(list)
        for nat, name, age in rows:
            key = nat.lower()
            if len(result[key]) < 2:
                result[key].append(name)
        return dict(result)

def report_top_hobbies():
    with get_session() as session:
        sub = (
            select(Hobby.person_id, func.count(Hobby.hobby).label("cnt"))
            .group_by(Hobby.person_id)
            .subquery()
        )
        rows = session.execute(
            select(Person.full_name)
            .join(sub, sub.c.person_id == Person.id)
            .order_by(sub.c.cnt.desc(), Person.full_name.asc())
            .limit(3)
        ).all()
        return [r[0] for r in rows]

def report_avg_height_nationality_general():
    with get_session() as session:
        general = session.execute(
            select(func.avg(Physical.height_cm)).where(Physical.height_cm.isnot(None))
        ).scalar()
        general_val = round(general, 2) if general is not None else None

        rows = session.execute(
            select(Physical.nationality, func.avg(Physical.height_cm))
            .where(Physical.height_cm.isnot(None), Physical.nationality.isnot(None))
            .group_by(Physical.nationality)
        ).all()
        by_nat = {nat.lower(): round(avg, 2) for nat, avg in rows}
        return {"general": general_val, "nationalities": by_nat}