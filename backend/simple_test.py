from app import db
from app.models.user import User
from app.models.card import Card

print("Successfully imported User and Card models")
print("User model relationships:", [rel for rel in dir(User) if not rel.startswith('_')])
print("Card model relationships:", [rel for rel in dir(Card) if not rel.startswith('_')])

print("Test completed successfully!")
