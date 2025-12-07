from flask import Blueprint, request, jsonify
from backend import db
from backend.models import CourtDate
from backend.routes.auth_routes import token_required, require_roles

courtdate_bp = Blueprint("courtdate_bp", __name__, url_prefix="/courtdate")

@courtdate_bp.route("/add", methods=["POST"])
@token_required
@require_roles("Clerk", "Judge", "Admin")
def add_courtdate():
    data = request.json
    new_cd = CourtDate(
        Date=data.get("date"),
        Time=data.get("time"),
        Location=data.get("location"),
        CaseID=data.get("case_id")
    )
    db.session.add(new_cd)
    db.session.commit()
    return jsonify({"message": "Court date added", "id": new_cd.CourtDateID}), 201

@courtdate_bp.route("/all", methods=["GET"])
@token_required
def get_all():
    cds = CourtDate.query.all()
    return jsonify([{
        "CourtDateID": c.CourtDateID,
        "Date": c.Date.isoformat(),
        "Time": c.Time.strftime("%H:%M:%S"),
        "Location": c.Location,
        "CaseID": c.CaseID
    } for c in cds]), 200

@courtdate_bp.route("/update/<int:id>", methods=["PUT"])
@token_required
@require_roles("Clerk", "Judge", "Admin")
def update(id):
    cd = CourtDate.query.get_or_404(id)
    data = request.json
    cd.Date = data.get("date", cd.Date)
    cd.Time = data.get("time", cd.Time)
    cd.Location = data.get("location", cd.Location)
    cd.CaseID = data.get("case_id", cd.CaseID)
    db.session.commit()
    return jsonify({"message": "Court date updated"}), 200

@courtdate_bp.route("/delete/<int:id>", methods=["DELETE"])
@token_required
@require_roles("Judge", "Admin")
def delete(id):
    cd = CourtDate.query.get_or_404(id)
    db.session.delete(cd)
    db.session.commit()
    return jsonify({"message": "Court date deleted"}), 200
