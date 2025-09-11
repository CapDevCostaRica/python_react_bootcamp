from flask import Flask, Blueprint, request as flask_request, jsonify
import os, sys

CURR_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.abspath(os.path.join(CURR_DIR, '..', '..', '..'))
FRAMEWORK_DIR = os.path.join(ROOT_DIR, 'framework')
for p in (CURR_DIR, ROOT_DIR, FRAMEWORK_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

from marshmallow import ValidationError
from sqlalchemy import select
from config import get_session  # <- usa sesiones desde config
from app.models import odkeyo_ex2Person as Person
from schema import PeopleFindFiltersSchema
from service import (
    build_query,
    report_sushi_ramen,
    report_avg_weight_above_70_hair,
    report_most_common_food_overall,
    report_avg_weight_nationality_hair,
    report_top_oldest_nationality,
    report_top_hobbies,
    report_avg_height_nationality_general,
)

app = Flask(__name__)
people_bp = Blueprint("people", __name__, url_prefix="/people")


def _extract_filters(args):
    filters = {}
    for k in args.keys():
        if k.startswith("filters[") and k.endswith("]"):
            key = k[len("filters["):-1]
            vals = args.getlist(k)
            filters[key] = vals if len(vals) > 1 else vals[0]
    return filters

@people_bp.get("/find")
def find_people():
    filters = _extract_filters(flask_request.args)
    try:
        PeopleFindFiltersSchema().load(filters)
    except ValidationError:
        return jsonify({"success": True, "data": {"total": 0, "results": []}})

    stmt = build_query(filters)
    with get_session() as session:
        people = session.execute(stmt).scalars().all()
        names = [p.full_name for p in people]

    return jsonify({"success": True, "data": {"total": len(names), "results": names}})


@people_bp.get("/sushi_ramen")
def sushi_ramen():
    return jsonify({"success": True, "data": report_sushi_ramen()})


@people_bp.get("/avg_weight_above_70_hair")
def avg_weight_above_70_hair():
    return jsonify({"success": True, "data": report_avg_weight_above_70_hair()})


@people_bp.get("/most_common_food_overall")
def most_common_food_overall():
    return jsonify({"success": True, "data": report_most_common_food_overall()})


@people_bp.get("/avg_weight_nationality_hair")
def avg_weight_nationality_hair():
    return jsonify({"success": True, "data": report_avg_weight_nationality_hair()})


@people_bp.get("/top_oldest_nationality")
def top_oldest_nationality():
    return jsonify({"success": True, "data": report_top_oldest_nationality()})


@people_bp.get("/top_hobbies")
def top_hobbies():
    return jsonify({"success": True, "data": report_top_hobbies()})


@people_bp.get("/avg_height_nationality_general")
def avg_height_nationality_general():
    return jsonify({"success": True, "data": report_avg_height_nationality_general()})


app.register_blueprint(people_bp)