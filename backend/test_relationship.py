from app import create_app, db
from app.models.user import User
from app.models.card import Card

app = create_app()

with app.app_context():
    # Check if the models can be accessed without errors
    print("Testing User and Card relationship...")
    
    # Get all users
    users = User.query.all()
    print(f"Found {len(users)} users")
    
    # Get all cards
    cards = Card.query.all()
    print(f"Found {len(cards)} cards")
    
    # Test relationship
    if users:
        user = users[0]
        print(f"User: {user.username}")
        print(f"User has {len(user.cards)} cards")
        
        # Try to create a new card for this user
        new_card = Card(
            user_id=user.id,
            card_type="Visa",
            last_four="1234",
            expiry_date="12/2025",
            cardholder_name="Test User",
            is_default=False
        )
        
        db.session.add(new_card)
        db.session.commit()
        
        print("Successfully added a new card")
        print(f"User now has {len(user.cards)} cards")
        
        # Clean up - delete the test card
        db.session.delete(new_card)
        db.session.commit()
        print("Test card deleted")
    
    print("Relationship test completed successfully!")
