from flask import Blueprint, jsonify
from backend.models import Case, RescheduleRequest
from .auth_routes import token_required, require_roles

admin_bp = Blueprint("admin_bp", __name__, url_prefix="/admin")

@admin_bp.route("/stats", methods=["GET"])
@token_required
@require_roles("Judge", "Admin")
def stats():
    return jsonify({
        "cases": {
            "total": Case.query.count(),
            "open": Case.query.filter_by(Status="Open").count(),
            "closed": Case.query.filter_by(Status="Closed").count(),
            "pending": Case.query.filter_by(Status="Pending").count(),
        },
        "reschedule_requests": {
            "total": RescheduleRequest.query.count(),
            "pending": RescheduleRequest.query.filter_by(Status="Pending").count(),
            "approved": RescheduleRequest.query.filter_by(Status="Approved").count(),
            "denied": RescheduleRequest.query.filter_by(Status="Denied").count(),
        }
    }), 200
