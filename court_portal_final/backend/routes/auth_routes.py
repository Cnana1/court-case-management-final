from flask import Blueprint, request, jsonify, current_app
from backend import db
from backend.models import User
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps
from datetime import datetime, timedelta

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/auth")

SECRET_KEY = "your_secret_key"  # Use .env in production

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            return jsonify({"error": "Token is missing"}), 401
        token = token.split(" ")[1]
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user = User.query.get(data["user_id"])
            if not user:
                return jsonify({"error": "User not found"}), 401
            request.user = {"id": user.UserID, "role": user.Role}
        except Exception as e:
            return jsonify({"error": f"Token invalid: {str(e)}"}), 401
        return f(*args, **kwargs)
    return decorated

def require_roles(*roles):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if request.user["role"] not in roles:
                return jsonify({"error": "Forbidden: insufficient privileges"}), 403
            return f(*args, **kwargs)
        return wrapped
    return decorator

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    if not data:
        return jsonify({"error": "Missing data"}), 400
    if User.query.filter_by(Email=data["email"]).first():
        return jsonify({"error": "Email already exists"}), 400
    hashed_pw = generate_password_hash(data["password"])
    user = User(Name=data["name"], Email=data["email"], Password=hashed_pw, Role=data.get("role","Clerk"))
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully", "user_id": user.UserID}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    user = User.query.filter_by(Email=email).first()
    if user and check_password_hash(user.Password, password):
        token = jwt.encode({
            "user_id": user.UserID,
            "role": user.Role,
            "exp": datetime.utcnow() + timedelta(hours=8)
        }, SECRET_KEY, algorithm="HS256")
        return jsonify({
    "token": token,
    "user": {
        "id": user.UserID,
        "name": user.Name,
        "email": user.Email,
        "role": user.Role
    }
}), 200

    return jsonify({"error": "Invalid credentials"}), 401
