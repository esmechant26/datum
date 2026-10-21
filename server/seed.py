
from app import app
from models import db, User, Job


SAMPLE_USERS = [
    {
        "username": "demo_contractor",
        "email": "demo@example.com",
        "password": "DemoPassword123!",
        "jobs": [
            {
                "title": "Repair wooden fence",
                "description": "Replace four damaged fence posts",
                "status": "pending",
                "client_name": "Jane Smith",
                "address": "123 Main Street, Hudson, NY"
            },
            {
                "title": "Install garden beds",
                "description": "Build three cedar raised beds",
                "status": "scheduled",
                "client_name": "Alex Johnson",
                "address": "45 Oak Road, Hudson, NY"
            },
            {
                "title": "Clean gutters",
                "description": "Clean gutters and inspect downspouts",
                "status": "completed",
                "client_name": "Morgan Lee",
                "address": "78 Pine Lane, Hudson, NY"
            }
        ]
    },
    {
        "username": "demo_landscaper",
        "email": "landscaper@example.com",
        "password": "DemoPassword123!",
        "jobs": [
            {
                "title": "Spring property cleanup",
                "description": "Remove brush and fallen branches",
                "status": "in_progress",
                "client_name": "Taylor Brooks",
                "address": "10 County Route 7, Craryville, NY"
            },
            {
                "title": "Mow meadow",
                "description": "Cut overgrown meadow",
                "status": "scheduled",
                "client_name": "Sam Parker",
                "address": "22 Farm Road, Hillsdale, NY"
            },
            {
                "title": "Plant native shrubs",
                "description": "Install native shrubs along driveway",
                "status": "pending",
                "client_name": "Casey Miller",
                "address": "8 Maple Avenue, Hudson, NY"
            }
        ]
    }
]


def seed_database():
    with app.app_context():
        for sample in SAMPLE_USERS:
            existing_user = User.query.filter_by(
                username=sample["username"]
            ).first()

            if existing_user:
                print(f"Skipping existing user: {sample['username']}")
                continue

            user = User(
                username=sample["username"],
                email=sample["email"]
            )
            user.set_password(sample["password"])

            for job_data in sample["jobs"]:
                job = Job(**job_data)
                user.jobs.append(job)

            db.session.add(user)

        db.session.commit()
        print("Database seeding complete!")


if __name__ == "__main__":
    seed_database()
