from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from backend import db
from backend.models import RescheduleRequest
from backend.routes.auth_routes import token_required, require_roles

reschedule_bp = Blueprint("reschedule_bp", __name__, url_prefix="/reschedule")
ALLOWED_EXTENSIONS = {"pdf", "docx", "jpg", "jpeg", "png"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@reschedule_bp.route("/add", methods=["POST"])
@token_required
def add_request():
    form = request.form
    if not form:
        return jsonify({"error": "No form data provided"}), 400

    try:
        case_id = int(form.get("CaseID") or form.get("case_id"))
        new_date_str = form.get("NewDate") or form.get("new_date")
        new_date = datetime.strptime(new_date_str, "%Y-%m-%d").date()
        old_date_id = form.get("OldDateID")  # optional
        old_date_id = int(old_date_id) if old_date_id else None
    except Exception as e:
        return jsonify({"error": f"Bad input: {str(e)}"}), 400

    filename = None
    file = request.files.get("file")
    if file and file.filename:
        if not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed"}), 400
        filename = secure_filename(file.filename)
        upload_dir = current_app.config.get("UPLOAD_FOLDER")
        os.makedirs(upload_dir, exist_ok=True)
        file.save(os.path.join(upload_dir, filename))

    new_req = RescheduleRequest(
        CaseID=case_id,
        OldDateID=old_date_id,
        NewDate=new_date,
        FileAttachment=filename
    )
    db.session.add(new_req)
    db.session.commit()
    return jsonify({"message": "Reschedule request created", "RequestID": new_req.RequestID}), 201


@reschedule_bp.route("/all", methods=["GET"])
@token_required
def get_all_requests():
    results = []
    for r in RescheduleRequest.query.order_by(RescheduleRequest.CreatedAt.desc()).all():
        results.append({
            "RequestID": r.RequestID,
            "CaseID": r.CaseID,
            "OldDateID": r.OldDateID,
            "NewDate": r.NewDate.isoformat() if r.NewDate else None,
            "FileAttachment": r.FileAttachment,
            "Status": r.Status,
            "CreatedAt": r.CreatedAt.isoformat() if r.CreatedAt else None
        })
    return jsonify(results), 200

@reschedule_bp.route("/approve/<int:request_id>", methods=["PUT"])
@token_required
@require_roles("Clerk", "Judge", "Admin")
def approve_request(request_id):
    req = RescheduleRequest.query.get_or_404(request_id)
    req.Status = "Approved"
    db.session.commit()
    return jsonify({"message": f"Request {request_id} approved"}), 200

@reschedule_bp.route("/deny/<int:request_id>", methods=["PUT"])
@token_required
@require_roles("Clerk", "Judge", "Admin")
def deny_request(request_id):
    req = RescheduleRequest.query.get_or_404(request_id)
    req.Status = "Denied"
    db.session.commit()
    return jsonify({"message": f"Request {request_id} denied"}), 200

@reschedule_bp.route("/delete/<int:request_id>", methods=["DELETE"])
@token_required
@require_roles("Judge", "Admin")
def delete_request(request_id):
    req = RescheduleRequest.query.get_or_404(request_id)
    # Delete uploaded file if exists
    if req.FileAttachment:
        upload_dir = current_app.config.get("UPLOAD_FOLDER")
        file_path = os.path.join(upload_dir, req.FileAttachment)
        if os.path.exists(file_path):
            os.remove(file_path)
    db.session.delete(req)
    db.session.commit()
    return jsonify({"message": "Reschedule request deleted"}), 200
