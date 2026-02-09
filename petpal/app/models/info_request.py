from app import db
from datetime import datetime

class InfoRequest(db.Model):
    __tablename__ = "info_requests"

    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey("animals.id"), nullable=False)

    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
