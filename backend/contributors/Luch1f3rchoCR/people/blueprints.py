from flask import Blueprint, request, jsonify
from sqlalchemy import select, and_, func

from .app.database import SessionLocal
from .app.models import People, Favorite, Hobbies, Family, Studies

people_bp = Blueprint("people", __name__, url_prefix="/people")

def _coalesce_json():
    j = request.get_json(silent=True)
    return j if isinstance(j, dict) else {}

def _filters_from_request():
    q = {}
    for src in (request.args, request.form):
        for k in src:
            vals = src.getlist(k)
            q[k] = vals if len(vals) > 1 else vals[0]
    j = _coalesce_json()
    payload = j.get("filters") if isinstance(j.get("filters"), dict) else j
    if isinstance(payload, dict):
        for k, v in payload.items():
            q[k] = v
    return q

def _to_list(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]

def _nums(vs, as_int=True):
    out = []
    for x in _to_list(vs):
        s = str(x).strip()
        if s.replace(".", "", 1).lstrip("-").isdigit():
            out.append(int(float(s)) if as_int else float(s))
    return out

def _lc_values(vs):
    return [str(x).lower() for x in _to_list(vs) if x is not None and str(x) != ""]

@people_bp.route("/find", methods=["GET", "POST"])
def people_find():
    f = _filters_from_request()

    join_food  = "food" in f
    join_hobby = "hobby" in f
    join_fam   = "family" in f
    join_study = ("degree" in f) or ("institution" in f)

    stmt = select(People.full_name).distinct()
    if join_food:
        stmt = stmt.join(Favorite, Favorite.person_id == People.id)
    if join_hobby:
        stmt = stmt.join(Hobbies, Hobbies.person_id == People.id)
    if join_fam:
        stmt = stmt.join(Family, Family.person_id == People.id)
    if join_study:
        stmt = stmt.join(Studies, Studies.person_id == People.id)

    conds = []

    eye_vals = _lc_values(f.get("eye_color"))
    if eye_vals:
        conds.append(func.lower(People.eye_color).in_(eye_vals))

    hair_vals = _lc_values(f.get("hair_color"))
    if hair_vals:
        conds.append(func.lower(People.hair_color).in_(hair_vals))

    nat_vals = _lc_values(f.get("nationality"))
    if nat_vals:
        conds.append(func.lower(People.nationality).in_(nat_vals))

    ages = _nums(f.get("age"), as_int=True)
    if ages:
        conds.append(People.age.in_(ages))

    heights = _nums(f.get("height_cm"), as_int=True)
    if heights:
        conds.append(People.height_cm.in_(heights))

    weights = _nums(f.get("weight_kg"), as_int=True)
    if weights:
        conds.append(People.weight_kg.in_(weights))

    food_vals = _lc_values(f.get("food"))
    if food_vals:
        conds.append(func.lower(Favorite.food).in_(food_vals))

    hobby_vals = _lc_values(f.get("hobby"))
    if hobby_vals:
        conds.append(func.lower(Hobbies.hobby).in_(hobby_vals))

    fam_vals = _lc_values(f.get("family"))
    if fam_vals:
        conds.append(func.lower(Family.relation).in_(fam_vals))

    degree_vals = _lc_values(f.get("degree"))
    if degree_vals:
        conds.append(func.lower(Studies.degree).in_(degree_vals))

    inst_vals = _lc_values(f.get("institution"))
    if inst_vals:
        conds.append(func.lower(Studies.institution).in_(inst_vals))

    if conds:
        stmt = stmt.where(and_(*conds))

    with SessionLocal() as db:
        results = db.execute(stmt).scalars().all()

    return jsonify({"success": True, "data": {"total": len(results), "results": results}})

@people_bp.get("/sushi_ramen")
def people_sushi_ramen():
    sub = (
        select(Favorite.person_id)
        .where(func.lower(Favorite.food).in_(["sushi", "ramen"]))
        .group_by(Favorite.person_id)
        .having(func.count(func.distinct(func.lower(Favorite.food))) == 2)
        .subquery()
    )
    stmt = select(func.count()).select_from(sub)
    with SessionLocal() as db:
        total = db.execute(stmt).scalar() or 0
    return jsonify({"success": True, "data": int(total)})

@people_bp.get("/sushi")
def people_sushi():
    stmt = select(func.count(func.distinct(Favorite.person_id))).where(func.lower(Favorite.food) == "sushi")
    with SessionLocal() as db:
        total = db.execute(stmt).scalar() or 0
    return jsonify({"success": True, "data": int(total)})

@people_bp.get("/avg_weight_above_70_hair")
def avg_weight_above_70_hair():
    min_w = request.args.get("min", 70, type=int)
    stmt = select(People.hair_color, func.avg(People.weight_kg)).where(People.weight_kg > min_w).group_by(People.hair_color)
    with SessionLocal() as db:
        rows = db.execute(stmt).all()
    data = {(hc or ""): int(round(avg or 0)) for hc, avg in rows}
    return jsonify({"success": True, "data": data})

@people_bp.get("/most_common_food_overall")
def most_common_food_overall():
    stmt = select(Favorite.food, func.count(Favorite.id)).group_by(Favorite.food).order_by(func.count(Favorite.id).desc()).limit(1)
    with SessionLocal() as db:
        row = db.execute(stmt).first()
    return jsonify({"success": True, "data": (row.food if row else "")})

@people_bp.get("/avg_weight_nationality_hair")
def avg_weight_nationality_hair():
    stmt = select(People.nationality, People.hair_color, func.avg(People.weight_kg)).group_by(People.nationality, People.hair_color)
    with SessionLocal() as db:
        rows = db.execute(stmt).all()
    data = {f"{(nat or '').lower()}-{(hc or '').lower()}": int(round(avg or 0)) for nat, hc, avg in rows}
    return jsonify({"success": True, "data": data})

@people_bp.get("/top_oldest_nationality")
def top_oldest_nationality():
    subq = (
        select(
            People.full_name.label("full_name"),
            func.coalesce(People.nationality, "").label("nat"),
            func.row_number().over(partition_by=func.coalesce(People.nationality, ""), order_by=People.age.desc()).label("rk"),
        ).subquery()
    )
    stmt = select(subq.c.full_name, subq.c.nat).where(subq.c.rk <= 2).order_by(subq.c.nat.asc(), subq.c.rk.asc())
    with SessionLocal() as db:
        rows = db.execute(stmt).all()
    out = {}
    for full_name, nat in rows:
        key = (nat or "").lower()
        out.setdefault(key, []).append(full_name)
    return jsonify({"success": True, "data": out})

@people_bp.get("/top_hobbies")
def top_hobbies():
    stmt = (
        select(People.full_name, func.count(Hobbies.id))
        .join(Hobbies, Hobbies.person_id == People.id, isouter=True)
        .group_by(People.id, People.full_name)
        .order_by(func.count(Hobbies.id).desc(), People.full_name.asc())
        .limit(3)
    )
    with SessionLocal() as db:
        rows = db.execute(stmt).all()
    names = [full_name for full_name, _ in rows]
    return jsonify({"success": True, "data": names})

@people_bp.get("/avg_height_nationality_general")
def avg_height_nationality_general():
    with SessionLocal() as db:
        general = db.execute(select(func.avg(People.height_cm))).scalar()
        rows = db.execute(select(People.nationality, func.avg(People.height_cm)).group_by(People.nationality)).all()
    result = {"general": int(round(general or 0)), "nationalities": {str(nat or "").lower(): int(round(avg or 0)) for nat, avg in rows}}
    return jsonify({"success": True, "data": result})