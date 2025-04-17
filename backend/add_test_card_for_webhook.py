import sqlite3
import os
import sys
import uuid
from app.utils.encryption import encrypt_card_number

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Database connection
DB_PATH = os.path.join(current_dir, 'instance', 'ecommerce.db')

def add_test_card_for_webhook():
    """
    Add a test card with a unique subscription ID and an expired date to the database
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
        
        # Generate a unique subscription ID
        subscription_id = f"SUB-TEST-{uuid.uuid4().hex[:8].upper()}"
        
        # Encrypt the card details
        card_number = encrypt_card_number("4111111111111111")
        
        # Insert the test card with an expired date
        cursor.execute("""
            INSERT INTO cards (
                user_id, card_number, last_four, expiry_date, cardholder_name, 
                card_type, is_default, subscription_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            user_id, 
            card_number, 
            "1111",  # Last four digits of the card
            "2023-01",  # Expired date (January 2023)
            "Webhook Test User",
            "Visa",
            0,  # Not default
            subscription_id  # Unique subscription ID
        ))
        
        # Commit the changes
        conn.commit()
        
        # Get the ID of the inserted card
        card_id = cursor.lastrowid
        
        print(f"Test card added successfully with ID: {card_id}")
        print(f"User ID: {user_id}")
        print(f"Subscription ID: {subscription_id}")
        print(f"Expiry Date: 2023-01 (expired)")
        
        # Close the connection
        conn.close()
        
        # Return the subscription ID for use in the webhook test
        return subscription_id
    
    except Exception as e:
        print(f"Error adding test card: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return None

if __name__ == "__main__":
    subscription_id = add_test_card_for_webhook()
    if subscription_id:
        print("\nUse this subscription ID in your webhook test:")
        print(f"Subscription ID: {subscription_id}")
