import sqlite3
import os

# Get the path to the database file
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'ecommerce.db')

# Connect to the database
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row  # This enables column access by name
cursor = conn.cursor()

# Get all cards from the database
cursor.execute("SELECT id, card_type, last_four, expiry_date, cardholder_name, subscription_id FROM cards")
cards = cursor.fetchall()

# Print the cards
print(f"Found {len(cards)} cards in the database:")
for card in cards:
    print(f"Card ID: {card['id']}")
    print(f"  Card Type: {card['card_type']}")
    print(f"  Last Four: {card['last_four']}")
    print(f"  Expiry Date: {card['expiry_date']}")
    print(f"  Cardholder Name: {card['cardholder_name']}")
    print(f"  Subscription ID: {card['subscription_id']}")
    print()

# Close the connection
conn.close()
