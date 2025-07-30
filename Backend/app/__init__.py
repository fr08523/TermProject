import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

db = SQLAlchemy()

def create_app():
    load_dotenv()   # reads .env in Backend/
    app = Flask(__name__)
    CORS(app)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    JWTManager(app)

    from app.routes.auth import auth_bp
    from app.routes.api  import api_bp
    from app.routes.analytics import analytics_bp
    from app.routes.data_management import data_mgmt_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(api_bp,  url_prefix="/api")
    app.register_blueprint(analytics_bp, url_prefix="/analytics")
    app.register_blueprint(data_mgmt_bp, url_prefix="/data-management")

    return app

