
from functools import wraps

from flask import Blueprint, request, jsonify, session
from models import db, User, Job

jobs_bp = Blueprint("jobs", __name__)

ALLOWED_STATUSES = {
    "pending",
    "scheduled",
    "in_progress",
    "completed"
}


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")

        if not user_id or not db.session.get(User, user_id):
            session.clear()
            return jsonify({"error": "Authentication required"}), 401

        return func(*args, **kwargs)

    return wrapper


def serialize_job(job):
    return {
        "id": job.id,
        "title": job.title,
        "description": job.description,
        "status": job.status,
        "client_name": job.client_name,
        "address": job.address,
        "user_id": job.user_id
    }


@jobs_bp.route("/jobs", methods=["GET"])
@login_required
def get_jobs():
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=5, type=int)

    if page < 1 or per_page < 1 or per_page > 100:
        return jsonify({"error": "Invalid pagination parameters"}), 400

    pagination = (
        Job.query
        .filter_by(user_id=session["user_id"])
        .order_by(Job.id.asc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    return jsonify({
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
        "total_pages": pagination.pages,
        "items": [serialize_job(job) for job in pagination.items]
    }), 200


@jobs_bp.route("/jobs", methods=["POST"])
@login_required
def create_job():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Valid JSON body required"}), 400

    title = data.get("title")
    status = data.get("status", "pending")

    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "Job title is required"}), 400

    if not isinstance(status, str) or status not in ALLOWED_STATUSES:
        return jsonify({"error": "Invalid job status"}), 400

    optional_fields = ("description", "client_name", "address")

    for field in optional_fields:
        if data.get(field) is not None and not isinstance(data[field], str):
            return jsonify({"error": f"{field} must be a string"}), 400

    job = Job(
        title=title.strip(),
        description=data.get("description"),
        status=status,
        client_name=data.get("client_name"),
        address=data.get("address"),
        user_id=session["user_id"]
    )

    db.session.add(job)
    db.session.commit()

    return jsonify(serialize_job(job)), 201


@jobs_bp.route("/jobs/<int:job_id>", methods=["GET"])
@login_required
def get_job(job_id):
    job = Job.query.filter_by(
        id=job_id,
        user_id=session["user_id"]
    ).first()

    if not job:
        return jsonify({"error": "Job not found"}), 404

    return jsonify(serialize_job(job)), 200


@jobs_bp.route("/jobs/<int:job_id>", methods=["PATCH"])
@login_required
def update_job(job_id):
    job = Job.query.filter_by(
        id=job_id,
        user_id=session["user_id"]
    ).first()

    if not job:
        return jsonify({"error": "Job not found"}), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Valid JSON body required"}), 400

    allowed_fields = {
        "title",
        "description",
        "status",
        "client_name",
        "address"
    }

    if not any(field in data for field in allowed_fields):
        return jsonify({"error": "No valid fields provided"}), 400

    # Validate all provided fields before applying changes.
    updates = {}

    for field in allowed_fields:
        if field not in data:
            continue

        value = data[field]

        if field == "title":
            if not isinstance(value, str) or not value.strip():
                return jsonify({"error": "Job title cannot be empty"}), 400
            value = value.strip()

        elif field == "status":
            if not isinstance(value, str) or value not in ALLOWED_STATUSES:
                return jsonify({"error": "Invalid job status"}), 400

        elif value is not None and not isinstance(value, str):
            return jsonify({"error": f"{field} must be a string"}), 400

        updates[field] = value

    for field, value in updates.items():
        setattr(job, field, value)

    db.session.commit()

    return jsonify(serialize_job(job)), 200


@jobs_bp.route("/jobs/<int:job_id>", methods=["DELETE"])
@login_required
def delete_job(job_id):
    job = Job.query.filter_by(
        id=job_id,
        user_id=session["user_id"]
    ).first()

    if not job:
        return jsonify({"error": "Job not found"}), 404

    db.session.delete(job)
    db.session.commit()

    return "", 204
