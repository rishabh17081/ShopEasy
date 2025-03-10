from flask import request, jsonify
from marshmallow import ValidationError
from functools import wraps

def validate_with_schema(schema_class):
    """
    Decorator to validate request JSON with a Marshmallow schema
    
    Args:
        schema_class: Marshmallow Schema class
        
    Returns:
        Decorated function that validates request with schema
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            schema = schema_class()
            try:
                data = schema.load(request.json)
                # Add validated data to kwargs
                kwargs['data'] = data
            except ValidationError as err:
                return jsonify({"errors": err.messages}), 400
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator
