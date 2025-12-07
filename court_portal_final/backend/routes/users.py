from flask import Blueprint, jsonify
from backend.__init__ import db
from backend.models import User

bp_users = Blueprint("users", __name__, url_prefix="/users")

@bp_users.route("/attendees", methods=["GET"])
def get_attendees():
    try:
        # Make sure the role field exists exactly as "Attendee"
        attendees = User.query.filter_by(Role="Attendee").all()
        result = [{"UserID": u.UserID, "Name": u.Name} for u in attendees]
        return jsonify(result), 200
    except Exception as e:
        print("Error fetching attendees:", e)
        return jsonify({"error": "Failed to fetch attendees"}), 500
