from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from app import db
from app.models.user import User
from marshmallow import Schema, fields, validate, ValidationError

auth_bp = Blueprint('auth', __name__)

# Validation schemas
class RegistrationSchema(Schema):
    username = fields.String(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6))
    first_name = fields.String()
    last_name = fields.String()

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)

# Routes
@auth_bp.route('/register', methods=['POST'])
def register():
    schema = RegistrationSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "Email already registered"}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"message": "Username already taken"}), 400
    
    # Create new user
    new_user = User(
        email=data['email'],
        username=data['username'],
        password_hash=User.generate_hash(data['password']),
        first_name=data.get('first_name'),
        last_name=data.get('last_name')
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    # Generate tokens
    access_token = create_access_token(identity=new_user.id)
    refresh_token = create_refresh_token(identity=new_user.id)
    
    return jsonify({
        "message": "User registered successfully",
        "user": new_user.to_dict(),
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    schema = LoginSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if user and User.verify_hash(data['password'], user.password_hash):
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            "message": "Login successful",
            "user": user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token
        }), 200
    
    return jsonify({"message": "Invalid credentials"}), 401

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)
    
    print(f"Refreshed token for user ID: {current_user_id}")
    
    return jsonify({
        "access_token": access_token
    }), 200

# Special route for demo token validation
@auth_bp.route('/validate-demo-token', methods=['GET'])
def validate_demo_token():
    auth_header = request.headers.get('Authorization')
    
    print(f"Validating demo token: {auth_header}")
    
    # Check if the header contains the demo token
    if auth_header and 'Bearer demo-jwt-token' in auth_header:
        # Return user ID 1 for John Doe
        return jsonify({
            "user_id": 1,
            "message": "Demo token validated"
        }), 200
    
    return jsonify({"message": "Invalid demo token"}), 401

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_user_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    return jsonify({
        "user": user.to_dict()
    }), 200
