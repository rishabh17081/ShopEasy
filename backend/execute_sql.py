import sqlite3
import os

# Get the path to the database file
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'ecommerce.db')

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Execute the SQL command to add the subscription_id column
try:
    cursor.execute("ALTER TABLE cards ADD COLUMN subscription_id VARCHAR(100)")
    print("Successfully added subscription_id column to cards table")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("Column subscription_id already exists in cards table")
    else:
        print(f"Error adding subscription_id column: {e}")

# Commit the changes and close the connection
conn.commit()
conn.close()
