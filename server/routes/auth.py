from flask import Blueprint, request, jsonify, session
from sqlalchemy.exc import IntegrityError

from models import db, User

auth_bp = Blueprint("auth", __name__)


def serialize_user(user):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email
    }


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Valid JSON body required"}), 400

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if (
        not isinstance(username, str)
        or not username.strip()
        or not isinstance(email, str)
        or not email.strip()
        or not isinstance(password, str)
        or not password
    ):
        return jsonify({"error": "Username, email, and password are required"}), 400

    username = username.strip()
    email = email.strip().lower()

    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 409

    user = User(username=username, email=email)
    user.set_password(password)

    db.session.add(user)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Username or email already exists"}), 409

    session.clear()
    session["user_id"] = user.id

    return jsonify(serialize_user(user)), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Valid JSON body required"}), 400

    username = data.get("username")
    password = data.get("password")

    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify({"error": "Username and password are required"}), 400

    user = User.query.filter_by(username=username.strip()).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid username or password"}), 401

    session.clear()
    session["user_id"] = user.id

    return jsonify(serialize_user(user)), 200


@auth_bp.route("/check_session", methods=["GET"])
def check_session():
    user_id = session.get("user_id")

    if not user_id:
        return "", 204

    user = db.session.get(User, user_id)

    if not user:
        session.clear()
        return "", 204

    return jsonify(serialize_user(user)), 200


@auth_bp.route("/logout", methods=["DELETE"])
def logout():
    session.clear()
    return "", 204