print("Starting import test...")

try:
    from app.models.user import User
    print("Successfully imported User model")
except Exception as e:
    print(f"Error importing User model: {e}")

try:
    from app.models.card import Card
    print("Successfully imported Card model")
except Exception as e:
    print(f"Error importing Card model: {e}")

print("Import test completed")
