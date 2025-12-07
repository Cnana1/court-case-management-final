from flask import Blueprint, request, jsonify 
from backend import db
from backend.models import Case, CaseAttendee
from backend.routes.auth_routes import token_required, require_roles

case_bp = Blueprint("case_bp", __name__, url_prefix="/cases")

# --------------------------------------------------
# CREATE CASE + ASSIGN ATTENDEES
# --------------------------------------------------
@case_bp.route("/add", methods=["POST"])
@token_required
@require_roles("Clerk", "Judge", "Admin")
def add_case():
    data = request.json

    new_case = Case(
        Description=data.get("description"),
        Status=data.get("status", "Open")
    )

    db.session.add(new_case)
    db.session.commit()  # commit first to generate CaseID

    attendee_ids = data.get("attendees", [])
    for uid in attendee_ids:
        db.session.add(CaseAttendee(CaseID=new_case.CaseID, UserID=uid))

    db.session.commit()

    # Return the full case object
    return jsonify({
        "CaseID": new_case.CaseID,
        "Description": new_case.Description,
        "Status": new_case.Status,
        "Attendees": [
            {"UserID": ca.UserID, "Name": ca.user.Name}
            for ca in new_case.assigned_attendees
        ]
    }), 201


# --------------------------------------------------
# GET ALL CASES WITH ASSIGNED ATTENDEES
# --------------------------------------------------
@case_bp.route("", methods=["GET"])
@token_required
def get_cases():
    cases = Case.query.all()
    result = []

    for c in cases:

        # Include ALL court dates for judges, clerks, admin
        court_dates = [
            {
                "CourtDateID": cd.CourtDateID,
                "Date": cd.Date.isoformat(),
                "Time": cd.Time.strftime("%H:%M"),
                "Location": cd.Location
            }
            for cd in c.court_dates
        ]

        result.append({
            "CaseID": c.CaseID,
            "Description": c.Description,
            "Status": c.Status,
            "CourtDates": court_dates,   # 🔥 ADDED THIS
            "Attendees": [
                {"UserID": ca.UserID, "Name": ca.user.Name}
                for ca in c.assigned_attendees
            ]
        })

    return jsonify(result), 200



# --------------------------------------------------
# UPDATE CASE + UPDATE ATTENDEES
# --------------------------------------------------
@case_bp.route("/update/<int:id>", methods=["PUT"])
@token_required
@require_roles("Clerk", "Judge", "Admin")
def update_case(id):
    case = Case.query.get_or_404(id)
    data = request.json

    case.Description = data.get("description", case.Description)
    case.Status = data.get("status", case.Status)

    # Update attendees if provided
    if "attendees" in data:
        new_list = set(data["attendees"])

        # Remove old entries
        CaseAttendee.query.filter_by(CaseID=id).delete()

        # Add updated attendees
        for uid in new_list:
            db.session.add(CaseAttendee(CaseID=id, UserID=uid))

    db.session.commit()

    # Return full updated case with attendees
    updated_case = {
        "CaseID": case.CaseID,
        "Description": case.Description,
        "Status": case.Status,
        "Attendees": [
            {"UserID": ca.UserID, "Name": ca.user.Name}
            for ca in case.assigned_attendees
        ]
    }

    return jsonify(updated_case), 200



# --------------------------------------------------
# DELETE CASE
# --------------------------------------------------
@case_bp.route("/delete/<int:id>", methods=["DELETE"])
@token_required
@require_roles("Judge", "Admin")
def delete_case(id):
    case = Case.query.get_or_404(id)
    db.session.delete(case)
    db.session.commit()
    return jsonify({"message": "Case deleted"}), 200

@case_bp.route("/mine", methods=["GET"])
@token_required
def get_my_cases():
    my_user_id = request.user["id"]

    cases = (
        Case.query
        .join(CaseAttendee)
        .filter(CaseAttendee.UserID == my_user_id)
        .all()
    )

    result = []

    for c in cases:

        # FIX: return all dates for the case (not filtered by user_court_dates)
        court_dates = [
            {
                "CourtDateID": cd.CourtDateID,
                "Date": cd.Date.isoformat(),
                "Time": cd.Time.strftime("%H:%M"),
                "Location": cd.Location
            }
            for cd in c.court_dates
        ]

        result.append({
            "CaseID": c.CaseID,
            "Description": c.Description,
            "Status": c.Status,
            "CourtDates": court_dates,
            "Attendees": [
                {"UserID": ca.UserID, "Name": ca.user.Name}
                for ca in c.assigned_attendees
            ]
        })

    return jsonify(result), 200
