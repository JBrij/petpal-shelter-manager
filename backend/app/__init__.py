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

    # Import models after db is initialized
    from app.models import Animal
    from flask import render_template
    from app.routes.animals import animals_bp

    # Register blueprints
    app.register_blueprint(animals_bp)

    @app.route("/adopt")
    def adopt_page():
        return render_template("adopt.html")
    
    @app.route("/animal/<int:animal_id>")
    def animal_page(animal_id):
        return render_template("animal.html", animal_id=animal_id)


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
