import sqlite3
import os

# Database connection
current_dir = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(current_dir, 'instance', 'ecommerce.db')

def check_cards_schema():
    """
    Check the schema of the cards table
    """
    try:
        # Connect to the database
        print(f"Connecting to database at: {DB_PATH}")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # List all tables in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Tables in the database:")
        for table in tables:
            print(f"- {table[0]}")
        
        # Get the schema of the cards table
        print("\nCards table schema:")
        cursor.execute("PRAGMA table_info(cards)")
        columns = cursor.fetchall()
        
        if not columns:
            print("No columns found for the cards table.")
        else:
            for column in columns:
                print(f"Column {column[0]}: {column[1]} ({column[2]})")
        
        # Close the connection
        conn.close()
    
    except Exception as e:
        print(f"Error checking cards schema: {str(e)}")
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_cards_schema()
