import sqlite3
import os

# Get the path to the database file
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'ecommerce.db')

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get the schema of the cards table
cursor.execute("PRAGMA table_info(cards)")
columns = cursor.fetchall()

# Print the schema
print("Schema of cards table:")
for column in columns:
    print(f"{column[0]}: {column[1]} ({column[2]})")

# Close the connection
conn.close()
