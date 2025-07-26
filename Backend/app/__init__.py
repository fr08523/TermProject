from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from database import db
from .auth import auth as auth_blueprint

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config['SECRET_KEY'] = 'your-secret-key'  # TODO: Change this to a strong, unique key in production!
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:@localhost:5432/sms'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    JWTManager(app)

    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
