import sqlite3
import os
import json
import uuid
from datetime import datetime

# Get the path to the database file
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'ecommerce.db')

# Connect to the database
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row  # This enables column access by name
cursor = conn.cursor()

# Function to create a mock subscription for a card
def create_subscription(card_number, expiry_date):
    """
    Create a mock PayPal Account Updater subscription for a card
    
    Args:
        card_number: The card number (PAN)
        expiry_date: The expiry date in MM/YY or MM/YYYY format
        
    Returns:
        dict: The subscription details including subscription_id
    """
    # Generate a unique subscription ID with SUB- followed by a 10-digit random number
    import random
    random_number = ''.join([str(random.randint(0, 9)) for _ in range(10)])
    subscription_id = f"SUB-{random_number}"
    
    # Get the last four digits of the card number
    last_four = card_number[-4:] if card_number else "0000"
    
    # Mock response similar to what PayPal would return
    response = {
        "external_account_id": f"EX-{last_four}{datetime.now().strftime('%Y%m%d')}",
        "merchant_id": "BT-MER-123",
        "account_category": "ANONYMOUS",
        "subscription_id": subscription_id,
        "subscription_status": "ACCEPTED",
        "registration_details": {
            "registration_id": f"MDAwMDAxMTAwMQ{last_four}",
            "registration_status": "ACCEPTED",
            "merchant_number": "98021",
            "vendor": "AMEX" if card_number.startswith(('34', '37')) else "VISA"
        },
        "links": [
            {
                "href": f"https://api.paypal.com/v1/payment-networks/account-status-subscriptions/{subscription_id}",
                "rel": "self",
                "method": "GET",
                "encType": "application/json"
            }
        ]
    }
    
    print(f"Created subscription for card ending in {last_four}")
    return response

# Get all cards from the database
cursor.execute("SELECT * FROM cards")
cards = cursor.fetchall()

print(f"Found {len(cards)} cards to subscribe")

# Subscribe each card to PayPal's Account Updater service
for card in cards:
    # In a real implementation, you would decrypt the card number
    # For this example, we'll use the encrypted card number as is
    card_number = card['card_number']
    expiry_date = card['expiry_date']
    
    # Create a subscription for the card
    subscription = create_subscription(card_number, expiry_date)
    
    # Update the card with the subscription ID
    cursor.execute(
        "UPDATE cards SET subscription_id = ? WHERE id = ?",
        (subscription['subscription_id'], card['id'])
    )
    
    print(f"Updated card {card['id']} with subscription ID {subscription['subscription_id']}")

# Commit the changes and close the connection
conn.commit()
conn.close()

print("All cards have been subscribed to PayPal's Account Updater service")
