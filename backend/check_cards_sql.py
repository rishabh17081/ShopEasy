import sqlite3
import os

# Database connection
current_dir = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(current_dir, 'instance', 'ecommerce.db')

def check_cards_with_subscription():
    """
    Check if there are any cards with subscription IDs in the database using direct SQL
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Query all cards with subscription IDs
        cursor.execute("SELECT * FROM cards WHERE subscription_id IS NOT NULL")
        cards = cursor.fetchall()
        
        if not cards:
            print("No cards with subscription IDs found in the database.")
            conn.close()
            return
        
        # Get column names
        cursor.execute("PRAGMA table_info(cards)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"Found {len(cards)} cards with subscription IDs:")
        for card in cards:
            card_dict = dict(zip(columns, card))
            print(f"Card ID: {card_dict['id']}")
            print(f"User ID: {card_dict['user_id']}")
            print(f"Card Number: {card_dict['card_number']}")
            print(f"Last Four: {card_dict['last_four']}")
            print(f"Expiry Date: {card_dict['expiry_date']}")
            print(f"Cardholder Name: {card_dict['cardholder_name']}")
            print(f"Card Type: {card_dict['card_type']}")
            print(f"Subscription ID: {card_dict['subscription_id']}")
            print("-" * 50)
        
        # Close the connection
        conn.close()
    
    except Exception as e:
        print(f"Error checking cards: {str(e)}")
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_cards_with_subscription()
