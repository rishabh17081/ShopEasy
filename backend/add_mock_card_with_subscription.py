import sys
import os
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.card import Card
from app.models.user import User
from app.utils.encryption import encrypt_card_number

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Database connection
DATABASE_URL = "sqlite:///instance/ecommerce.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def add_mock_card_with_subscription():
    """
    Add a mock card with a subscription ID and an expired date to the database
    """
    try:
        # Find a user to associate the card with
        user = session.query(User).first()
        print(f"Querying for users...")
        if not user:
            print("No users found in the database. Please create a user first.")
            return False
        
        print(f"Found user with ID: {user.id}")
        
        # Create a mock card with an expired date
        mock_card = Card(
            user_id=user.id,
            card_number=encrypt_card_number("4111111111111111"),  # Test card number
            cardholder_name="Test User",
            expiry_date="2023-01",  # Expired date
            cvv=encrypt_card_number("123"),
            card_type="Visa",
            subscription_id="SUB-8821123381"  # Mock subscription ID
        )
        
        # Add the card to the database
        session.add(mock_card)
        session.commit()
        
        print(f"Mock card added successfully with ID: {mock_card.id}")
        print(f"User ID: {mock_card.user_id}")
        print(f"Subscription ID: {mock_card.subscription_id}")
        print(f"Expiry Date: {mock_card.expiry_date}")
        
        return True
    
    except Exception as e:
        print(f"Error adding mock card: {str(e)}")
        session.rollback()
        return False
    
    finally:
        session.close()

if __name__ == "__main__":
    add_mock_card_with_subscription()
