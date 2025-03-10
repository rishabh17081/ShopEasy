from app import db
from datetime import datetime

class PaymentCard(db.Model):
    __tablename__ = 'payment_cards'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Card details (stored securely)
    card_last_four = db.Column(db.String(4), nullable=False)
    card_brand = db.Column(db.String(50), nullable=False)
    card_expiry_month = db.Column(db.String(2), nullable=False)
    card_expiry_year = db.Column(db.String(4), nullable=False)
    cardholder_name = db.Column(db.String(100), nullable=False)
    
    # PayPal Account Updater subscription
    paypal_subscription_id = db.Column(db.String(255), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_verified_at = db.Column(db.DateTime, nullable=True)
    
    # For soft deleting
    is_deleted = db.Column(db.Boolean, default=False)
    is_default = db.Column(db.Boolean, default=False)
    
    def to_dict(self, include_subscription=False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'card_last_four': self.card_last_four,
            'card_brand': self.card_brand,
            'card_expiry': f"{self.card_expiry_month}/{self.card_expiry_year}",
            'cardholder_name': self.cardholder_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_verified_at': self.last_verified_at.isoformat() if self.last_verified_at else None,
            'is_default': self.is_default
        }
        
        if include_subscription:
            data['paypal_subscription_id'] = self.paypal_subscription_id
            
        return data
