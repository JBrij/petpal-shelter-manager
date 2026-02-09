from flask_sqlalchemy import SQLAlchemy
from app import db  

class Animal(db.Model):
    __tablename__ = "animals"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    species = db.Column(db.String(50), nullable=False)

    # NEW: age split into value + unit
    age_value = db.Column(db.Integer)
    age_unit = db.Column(db.String(10))  # "weeks", "months", "years"

    status = db.Column(db.String(20), default="available")
    description = db.Column(db.Text)
    image_path = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
