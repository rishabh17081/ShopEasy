#!/usr/bin/env python3
import sqlite3
import json
import os
import re
from datetime import datetime, timedelta
import random

# Create database
def create_database():
    # Get the directory of the script and create db directory if it doesn't exist
    db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db')
    os.makedirs(db_dir, exist_ok=True)
    
    db_path = os.path.join(db_dir, 'ecommerce.db')
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Connect to the database (this will create it if it doesn't exist)
    conn = sqlite3.connect(db_path)
    return conn, db_path

# Create tables
def create_tables(conn):
    cursor = conn.cursor()
    
    # Create products table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        image TEXT,
        category TEXT,
        inventory INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        first_name TEXT,
        last_name TEXT,
        address TEXT,
        city TEXT,
        state TEXT,
        zip_code TEXT,
        country TEXT DEFAULT 'USA',
        phone TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP
    )
    ''')
    
    # Create cards table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cards (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        card_type TEXT NOT NULL,
        card_number TEXT NOT NULL,
        last_four TEXT NOT NULL,
        expiry_date TEXT NOT NULL,
        cardholder_name TEXT NOT NULL,
        is_default BOOLEAN DEFAULT 0,
        subscription_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Create orders table for future use
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'pending',
        total REAL NOT NULL,
        payment_method_id INTEGER,
        shipping_address TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (payment_method_id) REFERENCES cards (id)
    )
    ''')
    
    # Create order_items table for future use
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders (id),
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
    ''')
    
    conn.commit()


def read_products_json(file_path):
    """
    Read and parse product data from a JSON file.

    Args:
        file_path (str): Path to the JSON file

    Returns:
        list: List of product dictionaries
    """
    try:
        with open(file_path, 'r') as file:
            products = json.load(file)
        return products
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: Unable to parse JSON in '{file_path}'.")
        return []

# Extract product data from JavaScript file
def extract_products_from_js(js_file_path):
    with open(js_file_path, 'r') as file:
        js_content = file.read()

    
    try:
        file_path = "/Users/rishabhsharma/PycharmProjects/ecommerce-site/scripts/fixed_products.json"
        products = read_products_json(file_path)
        return products
    except json.JSONDecodeError as e:
        raise Exception(f"Error parsing products JSON: {e}")

# Insert products into the database
def insert_products(conn, products):
    cursor = conn.cursor()
    
    for product in products:
        cursor.execute('''
        INSERT INTO products (id, name, description, price, image, category, inventory)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            product['id'],
            product['name'],
            product['description'],
            product['price'],
            product['image'],
            product['category'],
            product['inventory']
        ))
    
    conn.commit()

# Create mock users
def create_mock_users(conn):
    cursor = conn.cursor()
    
    mock_users = [
        {
            'username': 'johndoe',
            'email': 'john.doe@example.com',
            'password_hash': 'hashed_password_123',  # In a real app, use proper password hashing
            'first_name': 'John',
            'last_name': 'Doe',
            'address': '123 Main St',
            'city': 'Boston',
            'state': 'MA',
            'zip_code': '02108',
            'phone': '555-123-4567',
            'last_login': (datetime.now() - timedelta(days=2)).isoformat()
        },
        {
            'username': 'janedoe',
            'email': 'jane.doe@example.com',
            'password_hash': 'hashed_password_456',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'address': '456 Oak Ave',
            'city': 'San Francisco',
            'state': 'CA',
            'zip_code': '94107',
            'phone': '555-987-6543',
            'last_login': datetime.now().isoformat()
        },
        {
            'username': 'bobsmith',
            'email': 'bob.smith@example.com',
            'password_hash': 'hashed_password_789',
            'first_name': 'Bob',
            'last_name': 'Smith',
            'address': '789 Pine Rd',
            'city': 'Chicago',
            'state': 'IL',
            'zip_code': '60611',
            'phone': '555-456-7890',
            'last_login': (datetime.now() - timedelta(days=5)).isoformat()
        },
        {
            'username': 'alicejones',
            'email': 'alice.jones@example.com',
            'password_hash': 'hashed_password_101',
            'first_name': 'Alice',
            'last_name': 'Jones',
            'address': '101 Elm St',
            'city': 'Seattle',
            'state': 'WA',
            'zip_code': '98101',
            'phone': '555-789-0123',
            'last_login': (datetime.now() - timedelta(days=1)).isoformat()
        },
        {
            'username': 'mikebrown',
            'email': 'mike.brown@example.com',
            'password_hash': 'hashed_password_202',
            'first_name': 'Mike',
            'last_name': 'Brown',
            'address': '202 Cedar Blvd',
            'city': 'Austin',
            'state': 'TX',
            'zip_code': '78701',
            'phone': '555-234-5678',
            'last_login': (datetime.now() - timedelta(hours=12)).isoformat()
        }
    ]
    
    for user in mock_users:
        cursor.execute('''
        INSERT INTO users (username, email, password_hash, first_name, last_name, 
                          address, city, state, zip_code, phone, last_login)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user['username'],
            user['email'],
            user['password_hash'],
            user['first_name'],
            user['last_name'],
            user['address'],
            user['city'],
            user['state'],
            user['zip_code'],
            user['phone'],
            user['last_login']
        ))
    
    conn.commit()
    return len(mock_users)

# Create mock payment cards using PayPal test cards
def create_mock_cards(conn, num_users):
    cursor = conn.cursor()
    
    # PayPal test cards from https://developer.paypal.com/tools/sandbox/card-testing/
    paypal_test_cards = [
        # Amex
        {'card_type': 'AMEX', 'card_number': '371449635398431', 'expiry_date': '01/2030'},
        {'card_type': 'AMEX', 'card_number': '371234806987034', 'expiry_date': '02/2028'},
    ]
    
    card_index = 0
    
    for user_id in range(1, 2):
        # Each user gets 1-3 cards
        num_cards = 2
        
        for i in range(num_cards):
            # Use PayPal test cards in sequence, cycling through them
            card = paypal_test_cards[card_index % len(paypal_test_cards)]
            card_index += 1
            
            card_type = card['card_type']
            card_number = card['card_number']
            expiry_date = card['expiry_date']
            
            # Get last four digits from the card number
            last_four = card_number[-4:]
            
            # Cardholder name based on user
            cursor.execute("SELECT first_name, last_name FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            cardholder_name = f"{user[0]} {user[1]}"
            
            # First card for each user is default
            is_default = 1 if i == 0 else 0
            
            # Leave subscription_id as NULL initially
            subscription_id = None
            
            cursor.execute('''
            INSERT INTO cards (user_id, card_type, card_number, last_four, expiry_date, cardholder_name, is_default, subscription_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                card_type,
                card_number,
                last_four,
                expiry_date,
                cardholder_name,
                is_default,
                subscription_id
            ))
    
    conn.commit()

# Main function to execute the script
def main():
    # Path to the JavaScript file with product data
    js_file_path = '/Users/rishabhsharma/PycharmProjects/ecommerce-site/frontend/src/services/productService.js'
    
    # Create the database
    conn, db_path = create_database()
    
    try:
        # Create tables
        create_tables(conn)
        
        # Extract products from JS file
        products = extract_products_from_js(js_file_path)
        
        # Insert products into database
        insert_products(conn, products)
        
        # Create mock users
        num_users = create_mock_users(conn)
        
        # Create mock payment cards
        create_mock_cards(conn, num_users)
        
        print(f"Database created successfully at: {db_path}")
        print(f"Added {len(products)} products")
        print(f"Added {num_users} users with payment cards")
        
        # Print sample queries to verify data
        cursor = conn.cursor()
        
        print("\nSample Products:")
        cursor.execute("SELECT id, name, price, category FROM products LIMIT 3")
        for row in cursor.fetchall():
            print(f"Product #{row[0]}: {row[1]} - ${row[2]} ({row[3]})")
        
        print("\nSample Users:")
        cursor.execute("SELECT id, username, email, first_name, last_name FROM users LIMIT 3")
        for row in cursor.fetchall():
            print(f"User #{row[0]}: {row[1]} ({row[3]} {row[4]}) - {row[2]}")
        
        print("\nSample Payment Cards:")
        cursor.execute("""
            SELECT c.id, u.username, c.card_type, c.card_number, c.last_four, c.expiry_date, c.is_default, c.subscription_id 
            FROM cards c
            JOIN users u ON c.user_id = u.id
            LIMIT 5
        """)
        for row in cursor.fetchall():
            default_status = "Default" if row[6] else "Additional"
            subscription_status = f", Subscription ID: {row[7]}" if row[7] else ", No subscription"
            print(f"Card #{row[0]}: {row[1]} - {row[2]} {row[3]} ending in {row[4]}, expires {row[5]} ({default_status}{subscription_status})")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
