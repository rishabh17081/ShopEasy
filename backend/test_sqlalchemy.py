print("Testing SQLAlchemy import...")

try:
    import sqlalchemy
    print(f"SQLAlchemy version: {sqlalchemy.__version__}")
    print("SQLAlchemy imported successfully")
except Exception as e:
    print(f"Error importing SQLAlchemy: {e}")

try:
    from flask_sqlalchemy import SQLAlchemy
    print("Flask-SQLAlchemy imported successfully")
except Exception as e:
    print(f"Error importing Flask-SQLAlchemy: {e}")

print("Test completed")
