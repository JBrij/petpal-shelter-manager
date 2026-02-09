import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app import db
from app.models import Animal
from app.models import AdoptionApplication
from flask import session

animals_bp = Blueprint("animals", __name__, url_prefix="/animals")

# Allowed image extensions
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def admin_required():
    return bool(session.get("admin_id"))

def normalize_age_unit(unit: str | None):
    if not unit:
        return None
    u = unit.strip().lower()
    allowed = {"weeks", "months", "years"}
    return u if u in allowed else None

def age_display(animal: Animal):
    if animal.age_value is None or not animal.age_unit:
        return None
    return f"{animal.age_value} {animal.age_unit}"

@animals_bp.route("/add", methods=["POST"])
def add_animal():
    if "name" not in request.form or "species" not in request.form:
        return jsonify({"error": "Name and species are required"}), 400

    name = request.form["name"]
    species = request.form["species"]

    age_value_raw = (request.form.get("age_value") or "").strip()
    age_unit = normalize_age_unit(request.form.get("age_unit"))

    status = request.form.get("status", "available")
    description = request.form.get("description")

    # Parse age_value
    age_value = None
    if age_value_raw != "":
        try:
            age_value = int(age_value_raw)
            if age_value < 0:
                return jsonify({"error": "Age value must be 0 or greater"}), 400
        except ValueError:
            return jsonify({"error": "Age value must be a number"}), 400

    # If one is provided, require both (optional, but user-friendly)
    if (age_value is None) != (age_unit is None):
        return jsonify({"error": "Please provide both age value and age unit (weeks/months/years)"}), 400

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
        age_value=age_value,
        age_unit=age_unit,
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
            "age_value": animal.age_value,
            "age_unit": animal.age_unit,
            "age_display": age_display(animal),
            "status": animal.status,
            "description": animal.description,
            # IMPORTANT: relative URL works locally + on Render
            "image_url": animal.image_path if animal.image_path else None
        })
    return {"animals": result}

@animals_bp.route("/<int:animal_id>", methods=["GET"])
def get_animal(animal_id):
    animal = Animal.query.get_or_404(animal_id)

    return {
        "id": animal.id,
        "name": animal.name,
        "species": animal.species,
        "age_value": animal.age_value,
        "age_unit": animal.age_unit,
        "age_display": age_display(animal),
        "status": animal.status,
        "description": animal.description,
        "image_url": animal.image_path if animal.image_path else None
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

@animals_bp.route("/applications", methods=["GET"])
def list_applications():
    apps = AdoptionApplication.query.order_by(AdoptionApplication.id.desc()).all()

    result = []
    for a in apps:
        animal = Animal.query.get(a.animal_id)

        result.append({
            "id": a.id,
            "animal_id": a.animal_id,
            "animal_name": animal.name if animal else "Unknown",
            "animal_species": animal.species if animal else None,
            "animal_image_url": (animal.image_path if animal and animal.image_path else None),
            "applicant_name": a.applicant_name,
            "email": a.email,
            "phone": a.phone,
            "message": a.message,
            "status": a.status
        })

    return {"applications": result}

@animals_bp.route("/applications/<int:app_id>/status", methods=["POST"])
def update_application_status(app_id):
    if not session.get("admin_id"):
        return jsonify({"error": "Unauthorized"}), 401

    app_obj = AdoptionApplication.query.get_or_404(app_id)

    data = request.get_json(silent=True) or {}
    new_status = (data.get("status") or "").strip().lower()

    allowed = {"pending", "approved", "denied"}
    if new_status not in allowed:
        return jsonify({"error": "Invalid status"}), 400

    # Update application
    app_obj.status = new_status

    # ALSO update the animal status so Adopt page reflects it
    animal = Animal.query.get(app_obj.animal_id)
    if animal:
        if new_status == "approved":
            animal.status = "adopted"

            # Deny other pending applications for same animal
            others = AdoptionApplication.query.filter(
                AdoptionApplication.animal_id == animal.id,
                AdoptionApplication.id != app_obj.id,
                AdoptionApplication.status == "pending"
            ).all()
            for o in others:
                o.status = "denied"
        else:
            approved_exists = AdoptionApplication.query.filter(
                AdoptionApplication.animal_id == animal.id,
                AdoptionApplication.status == "approved"
            ).first()
            animal.status = "adopted" if approved_exists else "available"

    db.session.commit()

    return jsonify({
        "message": "Status updated",
        "application_status": app_obj.status,
        "animal_status": animal.status if animal else None
    }), 200

# ADMIN: Update animal (edit)
@animals_bp.route("/<int:animal_id>/update", methods=["POST"])
def update_animal(animal_id):
    if not admin_required():
        return jsonify({"error": "Unauthorized"}), 401

    animal = Animal.query.get_or_404(animal_id)

    name = (request.form.get("name") or "").strip()
    species = (request.form.get("species") or "").strip()

    age_value_raw = (request.form.get("age_value") or "").strip()
    age_unit = normalize_age_unit(request.form.get("age_unit"))

    status = (request.form.get("status") or "").strip().lower()
    description = request.form.get("description")

    if not name or not species:
        return jsonify({"error": "Name and species are required"}), 400

    allowed_status = {"available", "pending", "adopted"}
    if status and status not in allowed_status:
        return jsonify({"error": "Invalid status"}), 400

    # Parse age_value
    age_value = None
    if age_value_raw != "":
        try:
            age_value = int(age_value_raw)
            if age_value < 0:
                return jsonify({"error": "Age value must be 0 or greater"}), 400
        except ValueError:
            return jsonify({"error": "Age value must be a number"}), 400

    # Require both or neither
    if (age_value is None) != (age_unit is None):
        return jsonify({"error": "Please provide both age value and age unit (weeks/months/years)"}), 400

    animal.name = name
    animal.species = species
    animal.age_value = age_value
    animal.age_unit = age_unit
    animal.status = status or animal.status
    animal.description = description

    # Optional: replace image
    image = request.files.get("image")
    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        upload_folder = os.path.join(current_app.root_path, "../../uploads")
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        image.save(filepath)
        animal.image_path = f"/uploads/{filename}"

    db.session.commit()

    return jsonify({"message": "Animal updated", "id": animal.id}), 200

# ADMIN: Delete animal
@animals_bp.route("/<int:animal_id>/delete", methods=["POST"])
def delete_animal(animal_id):
    if not admin_required():
        return jsonify({"error": "Unauthorized"}), 401

    animal = Animal.query.get_or_404(animal_id)

    # Optional: delete image file
    if animal.image_path:
        try:
            filename = animal.image_path.split("/uploads/")[-1]
            upload_folder = os.path.join(current_app.root_path, "../../uploads")
            filepath = os.path.join(upload_folder, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception:
            pass

    db.session.delete(animal)
    db.session.commit()

    return jsonify({"message": "Animal deleted"}), 200
