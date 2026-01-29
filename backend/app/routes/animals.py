import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app import db
from app.models import Animal
from app.models import AdoptionApplication

animals_bp = Blueprint("animals", __name__, url_prefix="/animals")

# Allowed image extensions
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@animals_bp.route("/add", methods=["POST"])
def add_animal():
    if "name" not in request.form or "species" not in request.form:
        return jsonify({"error": "Name and species are required"}), 400

    name = request.form["name"]
    species = request.form["species"]
    age = request.form.get("age")
    status = request.form.get("status", "available")
    description = request.form.get("description")

    # Handle image upload
    image = request.files.get("image")
    image_path = None
    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        upload_folder = os.path.join(current_app.root_path, "../../uploads")
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        image.save(filepath)
        image_path = f"/uploads/{filename}"

    # Create animal record
    animal = Animal(
        name=name,
        species=species,
        age=age,
        status=status,
        description=description,
        image_path=image_path
    )
    db.session.add(animal)
    db.session.commit()

    return jsonify({"message": "Animal added successfully", "id": animal.id}), 201

@animals_bp.route("/", methods=["GET"])
def get_animals():
    animals = Animal.query.all()
    result = []
    for animal in animals:
        result.append({
            "id": animal.id,
            "name": animal.name,
            "species": animal.species,
            "age": animal.age,
            "status": animal.status,
            "description": animal.description,
            "image_url": f"http://127.0.0.1:5000{animal.image_path}" if animal.image_path else None
        })
    return {"animals": result}

@animals_bp.route("/<int:animal_id>", methods=["GET"])
def get_animal(animal_id):
    animal = Animal.query.get_or_404(animal_id)

    return {
        "id": animal.id,
        "name": animal.name,
        "species": animal.species,
        "age": animal.age,
        "status": animal.status,
        "description": animal.description,
        "image_url": f"http://127.0.0.1:5000{animal.image_path}" if animal.image_path else None
    }

@animals_bp.route("/<int:animal_id>/apply", methods=["POST"])
def apply_for_animal(animal_id):
    Animal.query.get_or_404(animal_id)  # Ensure animal exists
    
    data = request.form

    if not data.get("name") or not data.get("email"):
        return jsonify({"error": "Name and email are required"}), 400

    application = AdoptionApplication(
        animal_id=animal_id,
        applicant_name=data["name"],
        email=data["email"],
        phone=data.get("phone"),
        message=data.get("message")
    )

    db.session.add(application)
    db.session.commit()

    return jsonify({"message": "Application submitted successfully"}), 201