from app import db
from datetime import datetime

class Card(db.Model):
    __tablename__ = 'cards'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    card_type = db.Column(db.String(50))
    last_four = db.Column(db.String(4), nullable=False)
    expiry_date = db.Column(db.String(7), nullable=False)  # Format: MM/YYYY or MM/YY
    cardholder_name = db.Column(db.String(100), nullable=False)
    is_default = db.Column(db.Boolean, default=False, nullable=False)
    subscription_id = db.Column(db.String(100), nullable=True)  # For PayPal Account Updater
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with user
    user = db.relationship('User', backref=db.backref('cards', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'card_type': self.card_type,
            'last_four': self.last_four,
            'expiry_date': self.expiry_date,
            'cardholder_name': self.cardholder_name,
            'is_default': self.is_default,
            'subscription_id': self.subscription_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
