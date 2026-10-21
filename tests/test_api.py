
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "server"))

from app import create_app
from models import db, User


@pytest.fixture
def client(tmp_path):
    app = create_app()
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{tmp_path / 'test.db'}",
        SECRET_KEY="testing-secret-key"
    )

    with app.app_context():
        db.create_all()

        with app.test_client() as client:
            yield client

        db.session.remove()
        db.drop_all()


def signup(client, username):
    return client.post("/signup", json={
        "username": username,
        "email": f"{username}@example.com",
        "password": "password123"
    })


def test_signup_and_password_hashing(client):
    response = signup(client, "contractor1")

    assert response.status_code == 201
    assert response.json["username"] == "contractor1"
    assert "password_hash" not in response.json

    with client.application.app_context():
        user = User.query.filter_by(username="contractor1").first()
        assert user is not None
        assert user.password_hash != "password123"
        assert user.check_password("password123")


def test_duplicate_signup(client):
    signup(client, "contractor1")

    response = signup(client, "contractor1")

    assert response.status_code == 409


def test_login_logout_and_session(client):
    signup(client, "contractor1")

    assert client.get("/check_session").status_code == 200

    response = client.delete("/logout")
    assert response.status_code == 204
    assert client.get("/check_session").status_code == 204

    response = client.post("/login", json={
        "username": "contractor1",
        "password": "password123"
    })

    assert response.status_code == 200
    assert client.get("/check_session").status_code == 200


def test_invalid_login(client):
    signup(client, "contractor1")
    client.delete("/logout")

    response = client.post("/login", json={
        "username": "contractor1",
        "password": "wrongpassword"
    })

    assert response.status_code == 401


def test_unauthorized_job_access(client):
    assert client.get("/jobs").status_code == 401
    assert client.post("/jobs", json={"title": "Test"}).status_code == 401
    assert client.get("/jobs/1").status_code == 401
    assert client.patch("/jobs/1", json={"status": "completed"}).status_code == 401
    assert client.delete("/jobs/1").status_code == 401


def test_job_crud(client):
    signup(client, "contractor1")

    response = client.post("/jobs", json={
        "title": "Repair fence",
        "description": "Replace damaged posts",
        "status": "pending",
        "client_name": "Jane Smith"
    })

    assert response.status_code == 201
    job_id = response.json["id"]

    response = client.get(f"/jobs/{job_id}")
    assert response.status_code == 200
    assert response.json["title"] == "Repair fence"

    response = client.patch(f"/jobs/{job_id}", json={
        "status": "completed"
    })

    assert response.status_code == 200
    assert response.json["status"] == "completed"

    response = client.delete(f"/jobs/{job_id}")
    assert response.status_code == 204

    assert client.get(f"/jobs/{job_id}").status_code == 404


def test_pagination(client):
    signup(client, "contractor1")

    for i in range(12):
        response = client.post("/jobs", json={
            "title": f"Job {i + 1}"
        })
        assert response.status_code == 201

    response = client.get("/jobs?page=2&per_page=5")

    assert response.status_code == 200
    assert response.json["page"] == 2
    assert response.json["per_page"] == 5
    assert response.json["total"] == 12
    assert response.json["total_pages"] == 3
    assert len(response.json["items"]) == 5


def test_user_cannot_access_another_users_jobs(client):
    signup(client, "contractor1")

    response = client.post("/jobs", json={
        "title": "Private contractor job"
    })
    assert response.status_code == 201
    job_id = response.json["id"]

    client.delete("/logout")
    signup(client, "contractor2")

    assert client.get(f"/jobs/{job_id}").status_code == 404

    assert client.patch(
        f"/jobs/{job_id}",
        json={"status": "completed"}
    ).status_code == 404

    assert client.delete(f"/jobs/{job_id}").status_code == 404

    response = client.get("/jobs")
    assert response.status_code == 200
    assert response.json["items"] == []

    client.delete("/logout")
    client.post("/login", json={
        "username": "contractor1",
        "password": "password123"
    })

    response = client.get(f"/jobs/{job_id}")
    assert response.status_code == 200
    assert response.json["status"] == "pending"


def test_invalid_job_data(client):
    signup(client, "contractor1")

    response = client.post("/jobs", json={"title": ""})
    assert response.status_code == 400

    response = client.post("/jobs", json={
        "title": "Test",
        "status": "invalid"
    })
    assert response.status_code == 400

    response = client.get("/jobs?page=0")
    assert response.status_code == 400
