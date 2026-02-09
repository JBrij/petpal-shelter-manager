from app import db
from datetime import datetime

class AdoptionApplication(db.Model):
    __tablename__ = "adoption_applications"

    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, nullable=False)
    applicant_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(50))
    message = db.Column(db.Text)
    status = db.Column(db.String(20), default="pending")
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
