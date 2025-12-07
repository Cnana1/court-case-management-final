from flask import Flask, current_app, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Upload folder for reschedule PDFs
    UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads", "reschedule_files")
    app.config["UPLOAD_FOLDER"] = UPLOAD_DIR
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB limit
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Database configuration
    DB_USER = "postgres"
    DB_PASSWORD = "Na05172004"
    DB_HOST = "127.0.0.1"
    DB_PORT = 5432
    DB_NAME = "courtportal"

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Import models BEFORE calling migrate.init_app
    from backend import models  # <--- IMPORTANT

    db.init_app(app)
    migrate.init_app(app, db)

    # Register routes
    from backend.routes import blueprints
    for bp in blueprints:
        prefix = f"/api"
        if bp.url_prefix:
            app.register_blueprint(bp, url_prefix=prefix + bp.url_prefix)
        else:
            app.register_blueprint(bp, url_prefix=prefix)

    @app.route("/")
    def home():
        return "Court Portal Backend is Running!"

    # Serve uploaded PDF files
    @app.route("/uploads/reschedule_files/<filename>")
    def uploaded_file(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    return app
