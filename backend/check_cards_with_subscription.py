import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.card import Card
from app.utils.encryption import decrypt_card_number

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Database connection
DATABASE_URL = "sqlite:///instance/ecommerce.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def list_cards_with_subscription():
    """
    List all cards with subscription IDs in the database
    """
    try:
        # Query all cards with subscription IDs
        cards = session.query(Card).filter(Card.subscription_id != None).all()
        
        if not cards:
            print("No cards with subscription IDs found in the database.")
            return
        
        print(f"Found {len(cards)} cards with subscription IDs:")
        for card in cards:
            # Decrypt the card number for display
            masked_card_number = "XXXX-XXXX-XXXX-" + decrypt_card_number(card.card_number)[-4:]
            
            print(f"Card ID: {card.id}")
            print(f"User ID: {card.user_id}")
            print(f"Card Number: {masked_card_number}")
            print(f"Cardholder Name: {card.cardholder_name}")
            print(f"Expiry Date: {card.expiry_date}")
            print(f"Card Type: {card.card_type}")
            print(f"Subscription ID: {card.subscription_id}")
            print("-" * 50)
    
    except Exception as e:
        print(f"Error listing cards: {str(e)}")
    
    finally:
        session.close()

if __name__ == "__main__":
    list_cards_with_subscription()
