import os
import tempfile
import pytest

from app import create_app, db
from app.models import Admin


@pytest.fixture()
def app():
    db_fd, db_path = tempfile.mkstemp()

    test_config = {
        "TESTING": True,
        "SECRET_KEY": "test-secret",
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    }

    app = create_app(test_config=test_config)

    with app.app_context():
        db.create_all()

        admin = Admin(username="admin")
        admin.set_password("password")
        db.session.add(admin)
        db.session.commit()

    yield app

    # --- teardown: close sqlite file cleanly on Windows ---
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.engine.dispose()

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture()
def client(app):
    return app.test_client()
