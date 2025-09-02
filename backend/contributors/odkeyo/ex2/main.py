from flask import Flask, Blueprint, request as flask_request, jsonify
import os, sys

CURR_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.abspath(os.path.join(CURR_DIR, '..', '..', '..'))
FRAMEWORK_DIR = os.path.join(ROOT_DIR, 'framework')

for p in (CURR_DIR, ROOT_DIR, FRAMEWORK_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

from marshmallow import ValidationError
from app.models import (
    Base,
    odkeyo_ex2Person as Person,
)
from config import get_engine
from schema import PeopleFindFiltersSchema
from service import (
    build_query,
    report_sushi_ramen, report_avg_weight_above_70_hair, report_most_common_food_overall,
    report_avg_weight_nationality_hair, report_top_oldest_nationality, report_top_hobbies,
    report_avg_height_nationality_general,
)

app = Flask(__name__)

if "ENGINE" not in app.config:
    app.config["ENGINE"] = get_engine()

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
    engine = app.config["ENGINE"]
    filters = _extract_filters(flask_request.args)
    try:
        PeopleFindFiltersSchema().load(filters)
    except ValidationError:
        return jsonify({"success": True, "data": {"total": 0, "results": []}})
    stmt = build_query(filters)
    from sqlalchemy.orm import Session
    with Session(engine) as session:
        people = session.execute(stmt).scalars().all()
        names = [p.full_name for p in people]
        return jsonify({"success": True, "data": {"total": len(names), "results": names}})

@people_bp.get("/sushi_ramen")
def sushi_ramen():
    engine = app.config["ENGINE"]
    return jsonify({"success": True, "data": report_sushi_ramen(engine)})

@people_bp.get("/avg_weight_above_70_hair")
def avg_weight_above_70_hair():
    engine = app.config["ENGINE"]
    return jsonify({"success": True, "data": report_avg_weight_above_70_hair(engine)})

@people_bp.get("/most_common_food_overall")
def most_common_food_overall():
    engine = app.config["ENGINE"]
    return jsonify({"success": True, "data": report_most_common_food_overall(engine)})

@people_bp.get("/avg_weight_nationality_hair")
def avg_weight_nationality_hair():
    engine = app.config["ENGINE"]
    return jsonify({"success": True, "data": report_avg_weight_nationality_hair(engine)})

@people_bp.get("/top_oldest_nationality")
def top_oldest_nationality():
    engine = app.config["ENGINE"]
    return jsonify({"success": True, "data": report_top_oldest_nationality(engine)})

@people_bp.get("/top_hobbies")
def top_hobbies():
    engine = app.config["ENGINE"]
    return jsonify({"success": True, "data": report_top_hobbies(engine)})

@people_bp.get("/avg_height_nationality_general")
def avg_height_nationality_general():
    engine = app.config["ENGINE"]
    return jsonify({"success": True, "data": report_avg_height_nationality_general(engine)})

app.register_blueprint(people_bp)