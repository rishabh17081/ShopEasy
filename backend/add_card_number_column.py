import sqlite3
import os

# Get the path to the database file
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'ecommerce.db')
print(f"Database path: {db_path}")

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if the card_number column already exists
cursor.execute("PRAGMA table_info(cards)")
columns = cursor.fetchall()
column_names = [column[1] for column in columns]

if 'card_number' not in column_names:
    print("Adding card_number column to cards table...")
    cursor.execute("ALTER TABLE cards ADD COLUMN card_number TEXT")
    print("Column added successfully.")
else:
    print("card_number column already exists.")

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database update complete")
