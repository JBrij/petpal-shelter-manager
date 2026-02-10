from app import db
from app.models import Animal, AdoptionApplication


def login_admin(client):
    return client.post("/admin/login", data={"username": "admin", "password": "password"}, follow_redirects=True)


def test_apply_requires_name_and_email(client, app):
    with app.app_context():
        animal = Animal(name="Buddy", species="Dog", status="available")
        db.session.add(animal)
        db.session.commit()
        animal_id = animal.id

    res = client.post(f"/animals/{animal_id}/apply", data={"name": ""})
    assert res.status_code == 400


def test_admin_required_for_application_status_update(client, app):
    with app.app_context():
        animal = Animal(name="Luna", species="Cat", status="available")
        db.session.add(animal)
        db.session.commit()

        application = AdoptionApplication(
            animal_id=animal.id,
            applicant_name="Test User",
            email="test@example.com",
            status="pending",
        )
        db.session.add(application)
        db.session.commit()
        app_id = application.id

    # Not logged in -> should be unauthorized
    res = client.post(f"/animals/applications/{app_id}/status", json={"status": "approved"})
    assert res.status_code in (401, 302)  # 302 if you redirect somewhere, 401 if API-style
