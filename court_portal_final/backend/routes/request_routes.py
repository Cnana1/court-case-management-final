from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from backend import db
from backend.models import Request as ReqModel
from backend.routes.auth_routes import token_required, require_roles

request_bp = Blueprint("request_bp", __name__, url_prefix="/request")

ALLOWED_EXTENSIONS = {"pdf", "docx", "jpg", "jpeg", "png"}
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@request_bp.route("/add", methods=["POST"])
@token_required
@require_roles("Clerk", "Judge", "Admin")
def add_request():
    data = request.form if request.form else request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    user_id = data.get("user_id") or data.get("UserID") or request.user["id"]
    case_id = data.get("case_id") or data.get("CaseID")
    reason = data.get("reason") or data.get("Reason")
    if not (user_id and case_id and reason):
        return jsonify({"error": "user_id, case_id, and reason required"}), 400

    filename = None
    if request.files:
        file = request.files.get("file")
        if file and file.filename:
            if not allowed_file(file.filename):
                return jsonify({"error": "File type not allowed"}), 400
            filename = secure_filename(file.filename)
            upload_dir = current_app.config.get("UPLOAD_FOLDER")
            os.makedirs(upload_dir, exist_ok=True)
            file.save(os.path.join(upload_dir, filename))

    new_req = ReqModel(
        UserID=int(user_id),
        CaseID=int(case_id),
        Reason=reason,
        FileUpload=filename
    )
    db.session.add(new_req)
    db.session.commit()
    return jsonify({"message": "Request created", "id": new_req.RequestID}), 201

@request_bp.route("/all", methods=["GET"])
@token_required
def get_all_requests():
    reqs = ReqModel.query.all()
    return jsonify([{
        "RequestID": r.RequestID,
        "UserID": r.UserID,
        "CaseID": r.CaseID,
        "Reason": r.Reason,
        "Status": r.Status,
        "FileUpload": r.FileUpload
    } for r in reqs]), 200

@request_bp.route("/update/<int:id>", methods=["PUT"])
@token_required
@require_roles("Clerk", "Judge", "Admin")  # All roles can approve/deny
def update_request(id):
    req = ReqModel.query.get_or_404(id)
    data = request.json
    # Only update status (approve/deny)
    req.Status = data.get("status", req.Status)
    db.session.commit()
    return jsonify({"message": "Request updated"}), 200

@request_bp.route("/delete/<int:id>", methods=["DELETE"])
@token_required
@require_roles("Judge", "Admin")
def delete_request(id):
    req = ReqModel.query.get_or_404(id)
    db.session.delete(req)
    db.session.commit()
    return jsonify({"message": "Request deleted"}), 200

