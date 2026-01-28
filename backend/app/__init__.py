from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from app.config import Config
import os

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)

    # Import models **after** db is initialized
    from app.models import Animal

    # Register blueprints
    from app.routes.animals import animals_bp
    app.register_blueprint(animals_bp)

    # Serve uploaded images
    @app.route("/uploads/<filename>")
    def uploaded_file(filename):
        upload_folder = os.path.join(app.root_path, "../../uploads")
        return send_from_directory(upload_folder, filename)

    # Home route
    @app.route("/")
    def home():
        return {"message": "PetPal API running"}

    # Create tables if they don't exist
    with app.app_context():
        db.create_all()

    return app
