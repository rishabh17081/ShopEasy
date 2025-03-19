import sqlite3
import os

# Get the path to the database file
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'ecommerce.db')
print(f"Database path: {db_path}")

# Remove the existing database file if it exists
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"Removed existing database file: {db_path}")

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create the users table first
print("Creating users table...")
cursor.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    first_name TEXT,
    last_name TEXT,
    address TEXT,
    city TEXT,
    state TEXT,
    zip_code TEXT,
    country TEXT,
    phone TEXT,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Insert a sample user (John Doe)
cursor.execute('''
INSERT INTO users (id, username, email, password_hash, first_name, last_name, address, city, state, zip_code, country, phone, last_login)
VALUES (2, 'johndoe', 'john.doe@gmail.com', 'hashed_password_123', 'John', 'Doe', '123 Main St', 'Boston', 'MA', '02108', 'USA', '555-123-4567', '2025-03-09T10:29:21.325127')
''')

cursor.execute('''
INSERT INTO users (id, username, email, password_hash, first_name, last_name, address, city, state, zip_code, country, phone, last_login)
VALUES (1, 'jamie', 'jamie.lee@gmail.com', 'hashed_password_123', 'Jamie', 'Lee', '134 Monroe St', 'Boston', 'MA', '02100', 'USA', '555-123-3467', '2025-03-09T10:29:21.325127')
''')
print("Sample user data inserted for John Doe (user_id = 1)")

# Create the cards table
print("Creating cards table...")
cursor.execute('''
CREATE TABLE cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    card_type TEXT,
    card_number TEXT,
    last_four TEXT NOT NULL,
    expiry_date TEXT NOT NULL,
    cardholder_name TEXT NOT NULL,
    is_default INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')

# Insert sample data for John Doe (user_id = 1)
cursor.execute('''
INSERT INTO cards (user_id, card_type, card_number, last_four, expiry_date, cardholder_name, is_default, created_at)
VALUES (2, 'AMEX', '371449635398431', '8431', '01/2030', 'John Doe', 1, '2025-03-11 17:29:21')
''')

cursor.execute('''
INSERT INTO cards (user_id, card_type, card_number, last_four, expiry_date, cardholder_name, is_default, created_at)
VALUES (2, 'AMEX', '371234806987034', '7034', '01/2024', 'John Doe', 0, '2025-03-11 17:29:21')
''')

print("Sample cards data inserted for John Doe (user_id = 1)")

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database setup complete")
