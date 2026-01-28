from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from app.config import Config

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)

    # Import models **after** db is created
    from app.models import Animal
    from app.routes.animals import animals_bp
    app.register_blueprint(animals_bp)

    @app.route("/")
    def home():
        return {"message": "PetPal API running"}

    return app
