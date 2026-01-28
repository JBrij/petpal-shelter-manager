import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app import db
from app.models import Animal

animals_bp = Blueprint("animals", __name__, url_prefix="/api/animals")

@animals_bp.route("", methods=["POST"])
def create_animal():
    name = request.form.get("name")
    species = request.form.get("species")
    age = request.form.get("age")
    description = request.form.get("description")
    image = request.files.get("image")

    image_path = None
    if image:
        filename = secure_filename(image.filename)
        save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        image.save(save_path)
        image_path = f"/uploads/{filename}"

    animal = Animal(
        name=name,
        species=species,
        age=age,
        description=description,
        image_path=image_path
    )

    db.session.add(animal)
    db.session.commit()

    return jsonify({"message": "Animal created"}), 201
