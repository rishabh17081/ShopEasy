from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager, get_jwt
from config import config_by_name
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_name='dev'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Custom JWT token validator for demo token
    # Note: We can't access request in these decorators directly
    # So we'll handle the demo token in the route handlers instead
    
    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(jwt_header, jwt_payload):
        # Here you would check if the token is in a blocklist
        # For now, we'll just allow all tokens
        return False
    
    @jwt.user_identity_loader
    def user_identity_lookup(user_id):
        # Just return the user ID as is
        return user_id
    
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        # Look up the user by ID
        identity = jwt_data["sub"]
        from app.models.user import User
        return User.query.get(identity)
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Import and register blueprints using the helper function
    from app.routes import register_routes
    register_routes(app)
    
    # Create a route to test the app
    @app.route('/api/health')
    def health_check():
        return {'status': 'healthy', 'message': 'E-commerce API is running!'}
    
    return app
