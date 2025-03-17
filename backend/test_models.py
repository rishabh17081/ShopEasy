print("Testing model relationships...")

try:
    from app.models.user import User
    from app.models.card import Card
    
    print("Models imported successfully")
    
    # Create test instances
    test_user = User(
        email="test@example.com",
        username="testuser",
        password_hash="test_hash",
        first_name="Test",
        last_name="User"
    )
    
    test_card = Card(
        user_id=1,  # This would be the user's ID in a real scenario
        card_type="Visa",
        last_four="1234",
        expiry_date="12/2025",
        cardholder_name="Test User",
        is_default=False
    )
    
    # Test relationship
    test_user.cards.append(test_card)
    print("Relationship test passed")
    
    # Test back-reference
    print(f"Card's user: {test_card.user}")
    
except Exception as e:
    print(f"Error: {e}")

print("Test completed")
