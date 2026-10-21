from flask import Flask
from flask_migrate import Migrate
from dotenv import load_dotenv

load_dotenv()

from config import Config
from models import db, bcrypt

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    if not app.config["SECRET_KEY"]:
        raise RuntimeError("SECRET_KEY must be set")

    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)

    @app.get("/")
    def index():
        return {"message": "Welcome to Datum API"}, 200

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)