import sqlite3
import os
import sys
from app.utils.encryption import encrypt_card_number

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Database connection
DB_PATH = os.path.join(current_dir, 'instance', 'ecommerce.db')

def add_mock_card_with_subscription():
    """
    Add a mock card with a subscription ID and an expired date to the database using direct SQL
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Find a user to associate the card with
        cursor.execute("SELECT id FROM users LIMIT 1")
        user_result = cursor.fetchone()
        
        if not user_result:
            print("No users found in the database. Please create a user first.")
            conn.close()
            return False
        
        user_id = user_result[0]
        print(f"Found user with ID: {user_id}")
        
        # Encrypt the card details
        card_number = encrypt_card_number("4111111111111111")
        cvv = encrypt_card_number("123")
        
        # Insert the mock card with an expired date
        cursor.execute("""
            INSERT INTO cards (
                user_id, card_number, last_four, expiry_date, cardholder_name, 
                card_type, is_default, subscription_id, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """, (
            user_id, 
            card_number, 
            "1111",  # Last four digits of the card
            "2023-01",  # Expired date
            "Test User",
            "Visa",
            0,  # Not default
            "SUB-8821123381"  # Mock subscription ID
        ))
        
        # Commit the changes
        conn.commit()
        
        # Get the ID of the inserted card
        card_id = cursor.lastrowid
        
        print(f"Mock card added successfully with ID: {card_id}")
        print(f"User ID: {user_id}")
        print(f"Subscription ID: SUB-8821123381")
        print(f"Expiry Date: 2023-01")
        
        # Close the connection
        conn.close()
        
        return True
    
    except Exception as e:
        print(f"Error adding mock card: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    add_mock_card_with_subscription()
