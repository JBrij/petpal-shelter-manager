from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from app.config import Config
import os

db = SQLAlchemy()
jwt = JWTManager()

def create_app(test_config=None):
    app = Flask(__name__)

    if test_config:
        app.config.update(test_config)
    else:
        app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)

    # Import models after db is initialized
    from app.models import Animal, Admin
    from app.routes.animals import animals_bp
    from flask import render_template, request, redirect, session, url_for
    from app.auth.utils import login_required

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
        return render_template("homepage.html")


    # Create tables if they don't exist
    with app.app_context():
        db.create_all()

    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")

            admin = Admin.query.filter_by(username=username).first()
            if admin and admin.check_password(password):
                session["admin_id"] = admin.id
                return redirect("/admin/applications")

            return render_template("admin_login.html", error="Invalid username or password")

        return render_template("admin_login.html", error=None)

    @app.route("/admin/logout")
    def admin_logout():
        session.pop("admin_id", None)
        return redirect("/admin/login")

    @app.route("/admin/applications")
    @login_required
    def admin_applications_page():
        return render_template("admin_applications.html")
    
    @app.route("/admin/add-animal")
    @login_required
    def admin_add_animal_page():
        return render_template("admin_add_animal.html")
    
    @app.route("/admin/animals")
    @login_required
    def admin_manage_animals_page():
        return render_template("admin_manage_animals.html")
    
    @app.route("/admin/info-requests")
    @login_required
    def admin_info_requests_page():
        return render_template("admin_info_requests.html")




    
    

    return app
