from flask import Blueprint, request, jsonify
from sqlalchemy import select, and_, func

from .app.database import SessionLocal
from .app.models import People, Favorite, Hobbies, Family, Studies

people_bp = Blueprint("people", __name__, url_prefix="/people")

def _as_list(v):
    if v is None:
        return []
    if isinstance(v, (list, tuple)):
        return list(v)
    return [v]

def _maybe_json_dict(v):
    if not isinstance(v, str):
        return None
    s = v.strip()
    if not (s.startswith("{") and s.endswith("}")):
        return None
    try:
        import json
        obj = json.loads(s)
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None

def _filters_from_request():
    out = {}
    for k, vs in request.args.lists():
        out[k] = vs if len(vs) > 1 else vs[0]
    if request.form:
        for k, vs in request.form.lists():
            if k == "filters" and len(vs) == 1:
                j = _maybe_json_dict(vs[0])
                if isinstance(j, dict):
                    for kk, vv in j.items():
                        if kk not in out:
                            out[kk] = vv
                continue
            if k not in out:
                out[k] = vs if len(vs) > 1 else vs[0]
    body = request.get_json(silent=True)
    if isinstance(body, dict):
        if isinstance(body.get("filters"), dict):
            for kk, vv in body["filters"].items():
                out[kk] = vv if kk not in out else out[kk]
        for kk, vv in body.items():
            if kk != "filters" and kk not in out:
                out[kk] = vv
    return out

def _lc(s):
    return (s or "").lower()

def _ci_in(col, values):
    vals = [_lc(v) for v in _as_list(values) if v is not None]
    if not vals:
        return None
    return func.lower(col).in_(vals)

@people_bp.route("/find", methods=["GET", "POST"])
def people_find():
    q = _filters_from_request()
    filters = []

    need_fav   = "food" in q
    need_hobby = "hobby" in q
    need_fam   = "family" in q
    need_study = ("degree" in q) or ("institution" in q)

    stmt = select(People.full_name).select_from(People).distinct()

    if "eye_color"   in q: filters.append(_ci_in(People.eye_color,   q["eye_color"]))
    if "hair_color"  in q: filters.append(_ci_in(People.hair_color,  q["hair_color"]))
    if "nationality" in q: filters.append(_ci_in(People.nationality, q["nationality"]))

    if "age" in q:
        nums = []
        for v in _as_list(q["age"]):
            try:
                nums.append(int(str(v).strip()))
            except Exception:
                pass
        if nums:
            filters.append(People.age.in_(nums))

    if "height_cm" in q:
        nums = []
        for v in _as_list(q["height_cm"]):
            try:
                nums.append(int(str(v).strip()))
            except Exception:
                pass
        if nums:
            filters.append(People.height_cm.in_(nums))

    if "weight_kg" in q:
        nums = []
        for v in _as_list(q["weight_kg"]):
            try:
                nums.append(int(str(v).strip()))
            except Exception:
                pass
        if nums:
            filters.append(People.weight_kg.in_(nums))

    if need_fav:
        stmt = stmt.join(Favorite, Favorite.person_id == People.id)
        filters.append(_ci_in(Favorite.food, q.get("food")))
    if need_hobby:
        stmt = stmt.join(Hobbies, Hobbies.person_id == People.id)
        filters.append(_ci_in(Hobbies.hobby, q.get("hobby")))
    if need_fam:
        stmt = stmt.join(Family, Family.person_id == People.id)
        filters.append(_ci_in(Family.relation, q.get("family")))
    if need_study:
        stmt = stmt.join(Studies, Studies.person_id == People.id)
        if "degree" in q:
            filters.append(_ci_in(Studies.degree, q.get("degree")))
        if "institution" in q:
            filters.append(_ci_in(Studies.institution, q.get("institution")))

    filters = [f for f in filters if f is not None]
    if filters:
        stmt = stmt.where(and_(*filters))

    with SessionLocal() as db:
        results = db.execute(stmt).scalars().all()

    return jsonify({"success": True, "data": {"total": len(results), "results": results}})

@people_bp.get("/sushi_ramen")
def people_sushi_ramen():
    subq = (
        select(Favorite.person_id)
        .where(func.lower(Favorite.food).in_(["sushi", "ramen"]))
        .group_by(Favorite.person_id)
        .having(func.count(func.distinct(func.lower(Favorite.food))) == 2)
        .subquery()
    )
    stmt = select(func.count()).select_from(subq)
    with SessionLocal() as db:
        total = db.execute(stmt).scalar() or 0
    return jsonify({"success": True, "data": int(total)})

@people_bp.get("/sushi")
def people_sushi():
    stmt = (
        select(func.count(func.distinct(Favorite.person_id)))
        .where(func.lower(Favorite.food) == "sushi")
    )
    with SessionLocal() as db:
        total = db.execute(stmt).scalar() or 0
    return jsonify({"success": True, "data": int(total)})

@people_bp.get("/avg_weight_above_70_hair")
def avg_weight_above_70_hair():
    min_w = request.args.get("min", 70, type=int)
    stmt = (
        select(People.hair_color, func.avg(People.weight_kg))
        .where(People.weight_kg > min_w)
        .group_by(People.hair_color)
    )
    with SessionLocal() as db:
        rows = db.execute(stmt).all()
    data = {(hc or ""): int(round(avg or 0)) for hc, avg in rows}
    return jsonify({"success": True, "data": data})

@people_bp.get("/most_common_food_overall")
def most_common_food_overall():
    stmt = (
        select(Favorite.food, func.count(Favorite.id))
        .group_by(Favorite.food)
        .order_by(func.count(Favorite.id).desc())
        .limit(1)
    )
    with SessionLocal() as db:
        row = db.execute(stmt).first()
    return jsonify({"success": True, "data": (row.food if row else "")})

@people_bp.get("/avg_weight_nationality_hair")
def avg_weight_nationality_hair():
    stmt = (
        select(People.nationality, People.hair_color, func.avg(People.weight_kg))
        .group_by(People.nationality, People.hair_color)
    )
    with SessionLocal() as db:
        rows = db.execute(stmt).all()
    data = {f"{_lc(nat)}-{_lc(hc)}": int(round(avg or 0)) for nat, hc, avg in rows}
    return jsonify({"success": True, "data": data})

@people_bp.get("/top_oldest_nationality")
def top_oldest_nationality():
    subq = (
        select(
            People.full_name.label("full_name"),
            func.coalesce(People.nationality, "").label("nat"),
            func.row_number().over(
                partition_by=func.coalesce(People.nationality, ""),
                order_by=People.age.desc()
            ).label("rk")
        ).subquery()
    )
    stmt = (
        select(subq.c.full_name, subq.c.nat)
        .where(subq.c.rk <= 2)
        .order_by(subq.c.nat.asc(), subq.c.rk.asc())
    )
    with SessionLocal() as db:
        rows = db.execute(stmt).all()
    out = {}
    for full_name, nat in rows:
        key = _lc(nat)
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
        rows = db.execute(
            select(People.nationality, func.avg(People.height_cm)).group_by(People.nationality)
        ).all()
    result = {"general": int(round(general or 0)), "nationalities": {_lc(nat): int(round(avg or 0)) for nat, avg in rows}}
    return jsonify({"success": True, "data": result})