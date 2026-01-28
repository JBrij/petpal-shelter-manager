import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "petpal.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "dev-secret-change-later"
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "../uploads")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
