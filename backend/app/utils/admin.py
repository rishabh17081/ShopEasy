from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app.models.user import User

def admin_required(f):
    """
    Decorator to check if the current user is an admin
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not getattr(user, 'is_admin', False):
            return jsonify({
                "message": "Admin privileges required for this operation"
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function
