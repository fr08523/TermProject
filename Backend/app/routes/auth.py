from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app import db
from app.models.models import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.post("/register")
def register():
    data = request.get_json()
    if User.query.filter_by(username=data["username"]).first():
        return jsonify(msg="Username taken"), 409
    u = User(username=data["username"])
    u.set_password(data["password"])
    db.session.add(u)
    db.session.commit()
    return jsonify(msg="registered"), 201

@auth_bp.post("/login")
def login():
    data = request.get_json()
    u = User.query.filter_by(username=data["username"]).first()
    if not u or not u.check_password(data["password"]):
        return jsonify(msg="bad credentials"), 401

    # cast identity to string so JWT sub claim is valid
    token = create_access_token(identity=str(u.id))
    return jsonify(access_token=token)

