# Datum

A RESTful API for contractor job management, built with Python, Flask, SQLAlchemy, and SQLite.

Datum allows contractors to create accounts, securely log in, and manage their own jobs. Each contractor can create, view, update, and delete jobs without accessing another user's data.

## Features

- User registration with unique usernames and emails
- Secure password hashing with Flask-Bcrypt
- Session-based authentication
- Login, logout, and session verification
- Protected job management endpoints
- Full CRUD functionality for jobs
- Paginated job listings
- User-specific authorization
- Input validation and error handling
- Database migrations using Flask-Migrate
- Sample database seeding
- Automated API testing with pytest

## Tech Stack

- Python
- Flask
- Flask-SQLAlchemy
- SQLAlchemy
- Flask-Bcrypt
- Flask-Migrate
- SQLite
- python-dotenv
- pytest
- Pipenv

## Project Structure

```text
datum/
├── server/
│   ├── app.py
│   ├── config.py
│   ├── models.py
│   ├── seed.py
│   ├── migrations/
│   └── routes/
│       ├── __init__.py
│       ├── auth.py
│       └── jobs.py
├── tests/
│   └── test_api.py
├── .gitignore
├── Pipfile
├── Pipfile.lock
└── README.md
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/esmechant26/datum.git
cd datum
```

### 2. Install dependencies

Make sure Python and Pipenv are installed.

```bash
pipenv install --dev
```

### 3. Configure environment variables

Create a `.env` file in the project root.

Add a secret key:

```env
SECRET_KEY=replace_with_a_secure_random_secret_key
```

Generate a secure key using:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Copy the generated key into `.env`.

The `.env` file should not be committed to Git.

### 4. Initialize the database

Run the migrations:

```bash
cd server
pipenv run flask --app app db upgrade
cd ..
```

This creates the SQLite database and applies the existing migrations.

### 5. Seed sample data

From the project root:

```bash
pipenv run python server/seed.py
```

The seed script creates two demonstration contractors and six sample jobs.

Demo credentials:

Username: `demo_contractor`

Password: `DemoPassword123!`

These credentials are intended for local development only.

### 6. Start the server

From the project root:

```bash
pipenv run flask --app server/app.py run --debug --port 5001
```

The API will be available at:

http://127.0.0.1:5001

Port 5001 is used for local development to avoid potential conflicts with services using port 5000.

## API Endpoints

### Authentication

| Method | Endpoint         | Description           | Authentication |
| ------ | ---------------- | --------------------- | -------------- |
| POST   | `/signup`        | Register a new user   | No             |
| POST   | `/login`         | Log in                | No             |
| GET    | `/check_session` | Retrieve current user | Session        |
| DELETE | `/logout`        | Log out               | No             |

### Jobs

| Method | Endpoint     | Description             |
| ------ | ------------ | ----------------------- |
| GET    | `/jobs`      | Retrieve paginated jobs |
| GET    | `/jobs/<id>` | Retrieve a specific job |
| POST   | `/jobs`      | Create a job            |
| PATCH  | `/jobs/<id>` | Update a job            |
| DELETE | `/jobs/<id>` | Delete a job            |

All job endpoints require authentication.

Users can only retrieve, update, or delete jobs belonging to their own account.

## Data Models

### User

| Field         | Description     |
| ------------- | --------------- |
| id            | Primary key     |
| username      | Unique username |
| email         | Unique email    |
| password_hash | Hashed password |

A user has many jobs.

### Job

| Field       | Description                  |
| ----------- | ---------------------------- |
| id          | Primary key                  |
| title       | Required job title           |
| description | Optional job description     |
| status      | Current job status           |
| client_name | Client name                  |
| address     | Job location                 |
| user_id     | Foreign key to the job owner |

Supported job statuses:

- `pending`
- `scheduled`
- `in_progress`
- `completed`

A job belongs to one user.

## API Examples

### Register a user

```bash
curl -X POST http://127.0.0.1:5001/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "contractor",
    "email": "contractor@example.com",
    "password": "password123"
  }'
```

### Log in

Use a cookie file to preserve the authenticated session:

```bash
curl -c cookies.txt \
  -X POST http://127.0.0.1:5001/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "contractor",
    "password": "password123"
  }'
```

### Create a job

```bash
curl -b cookies.txt \
  -X POST http://127.0.0.1:5001/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Repair garden fence",
    "description": "Replace damaged fence posts",
    "status": "pending",
    "client_name": "Jane Smith",
    "address": "Hudson, NY"
  }'
```

The job is automatically assigned to the authenticated user.

### List jobs with pagination

```bash
curl -b cookies.txt \
  "http://127.0.0.1:5001/jobs?page=1&per_page=5"
```

Example response:

```json
{
  "page": 1,
  "per_page": 5,
  "total": 1,
  "total_pages": 1,
  "items": [
    {
      "id": 1,
      "title": "Repair garden fence",
      "description": "Replace damaged fence posts",
      "status": "pending",
      "client_name": "Jane Smith",
      "address": "Hudson, NY",
      "user_id": 1
    }
  ]
}
```

### Update a job

```bash
curl -b cookies.txt \
  -X PATCH http://127.0.0.1:5001/jobs/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'
```

### Delete a job

```bash
curl -b cookies.txt \
  -X DELETE http://127.0.0.1:5001/jobs/1
```

Successful deletion returns HTTP 204.

## Authentication and Security

Datum uses Flask sessions to authenticate users.

Passwords are hashed with Flask-Bcrypt before being stored in the database.

Protected routes require an authenticated session.

Each job is associated with a user through the `user_id` foreign key.

Job queries are restricted to the authenticated user's records. Unauthorized attempts to access another user's job return HTTP 404.

Unauthenticated requests to protected endpoints return HTTP 401.

The application uses environment variables for its secret key.

## Error Handling

The API uses standard HTTP status codes:

| Status | Meaning                                        |
| ------ | ---------------------------------------------- |
| 200    | Successful request                             |
| 201    | Resource created                               |
| 204    | Successful request with no response body       |
| 400    | Invalid request data                           |
| 401    | Authentication required or invalid credentials |
| 404    | Resource not found or inaccessible             |
| 409    | Duplicate username or email                    |

## Testing

Automated tests use pytest and an isolated temporary SQLite database.

From the project root:

```bash
pipenv run python -m pytest tests/ -v
```

The test suite includes:

- User registration and password hashing
- Duplicate username validation
- Login and logout
- Session verification
- Invalid credentials
- Protected route authentication
- Job creation, retrieval, updating, and deletion
- Pagination
- User ownership and authorization
- Invalid job data

The automated tests do not modify the development database.

## Future Development

Datum is designed as the backend foundation for a contractor management platform.

Potential future features include:

- Client and property management
- Job scheduling and calendars
- Estimates and invoicing
- File and photo uploads
- Automated reminders
- A React frontend
- Mobile-friendly contractor dashboards

## Author

Esme Chant

GitHub: https://github.com/esmechant26

```

```
