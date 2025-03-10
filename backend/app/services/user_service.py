from app import db
from app.models.user import User
from flask_jwt_extended import create_access_token, create_refresh_token

class UserService:
    @staticmethod
    def register_user(data):
        """
        Register a new user
        
        Args:
            data: Dictionary with user registration data
            
        Returns:
            Tuple of (user, tokens, error_message)
        """
        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return None, None, "Email already registered"
        
        if User.query.filter_by(username=data['username']).first():
            return None, None, "Username already taken"
        
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
        tokens = {
            'access_token': create_access_token(identity=new_user.id),
            'refresh_token': create_refresh_token(identity=new_user.id)
        }
        
        return new_user, tokens, None
    
    @staticmethod
    def login_user(email, password):
        """
        Authenticate and login a user
        
        Args:
            email: User's email
            password: User's password
            
        Returns:
            Tuple of (user, tokens, error_message)
        """
        user = User.query.filter_by(email=email).first()
        
        if user and User.verify_hash(password, user.password_hash):
            tokens = {
                'access_token': create_access_token(identity=user.id),
                'refresh_token': create_refresh_token(identity=user.id)
            }
            return user, tokens, None
        
        return None, None, "Invalid credentials"
    
    @staticmethod
    def get_user_by_id(user_id):
        """
        Get user by ID
        
        Args:
            user_id: User's ID
            
        Returns:
            User object or None
        """
        return User.query.get(user_id)
