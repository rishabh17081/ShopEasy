import sqlite3
import os

# Get the path to the database file
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'ecommerce.db')
print(f"Database path: {db_path}")

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if the users table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
if cursor.fetchone():
    print("Users table exists")
    
    # Get all users
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    print(f"Found {len(users)} users:")
    for user in users:
        print(user)
else:
    print("Users table does not exist")

# Check if the cards table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cards'")
if cursor.fetchone():
    print("Cards table exists")
    
    # Get all cards
    cursor.execute("SELECT * FROM cards")
    cards = cursor.fetchall()
    print(f"Found {len(cards)} cards:")
    for card in cards:
        print(card)
else:
    print("Cards table does not exist")

# Close the connection
conn.close()
