from flask import Blueprint, request, jsonify
from backend.routes.auth_routes import token_required, require_roles

schedule_bp = Blueprint("schedule", __name__, url_prefix="/schedule")


@schedule_bp.route("/test", methods=["GET"])
@token_required
def test_schedule():
    return jsonify({"message": "Fetched all schedules successfully!"})

@schedule_bp.route("/add", methods=["POST"])
@token_required
@require_roles("Judge", "Admin")
def add_schedule():
    data = request.json
    case_id = data.get("case_id")
    court_date = data.get("court_date")
    return jsonify({
        "message": "Schedule added!",
        "data": {"case_id": case_id, "court_date": court_date}
    }), 201
