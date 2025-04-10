import sys
import os
import logging
from app import db, create_app
from app.models.card import Card
from app.utils.encryption import decrypt_card_number
import requests
import json
from datetime import datetime

# Set up logging
logging.basicConfig(
    filename='card_subscriptions.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('card_subscription_manager')

def create_subscription(pan, expiry_date):
    """
    Create a PayPal Account Updater subscription for a card
    
    Args:
        pan: The card number (PAN)
        expiry_date: The expiry date in MM/YY or MM/YYYY format
        
    Returns:
        dict: The subscription details including subscription_id
    """
    try:
        # Convert expiry date to YYYY-MM format if needed
        if '/' in expiry_date:
            month, year = expiry_date.split('/')
            if len(year) == 2:
                year = f"20{year}"
            expiry_date = f"{year}-{month}"
        
        # In a real implementation, you would call PayPal's API here
        # For now, we'll simulate a response based on the PayPal AU Subscription Connector
        
        # Generate a unique subscription ID based on the last 4 digits of the card
        last_four = pan[-4:]
        subscription_id = f"SUB-{last_four}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Mock response similar to what PayPal would return
        response = {
            "external_account_id": f"EX-{last_four}{datetime.now().strftime('%Y%m%d')}",
            "merchant_id": "BT-MER-123",
            "account_category": "ANONYMOUS",
            "subscription_id": subscription_id,
            "subscription_status": "ACCEPTED",
            "registration_details": {
                "registration_id": f"MDAwMDAxMTAwMQ{last_four}",
                "registration_status": "ACCEPTED",
                "merchant_number": "98021",
                "vendor": "AMEX" if pan.startswith(('34', '37')) else "VISA"
            },
            "links": [
                {
                    "href": f"https://api.paypal.com/v1/payment-networks/account-status-subscriptions/{subscription_id}",
                    "rel": "self",
                    "method": "GET",
                    "encType": "application/json"
                }
            ]
        }
        
        logger.info(f"Created subscription for card ending in {last_four}")
        return response
    except Exception as e:
        logger.error(f"Error creating subscription: {str(e)}")
        return None

def subscribe_all_cards():
    """
    Subscribe all cards in the database to PayPal's Account Updater service
    """
    app = create_app()
    with app.app_context():
        try:
            # Get all cards that don't have a subscription ID
            cards = Card.query.filter(Card.subscription_id.is_(None)).all()
            logger.info(f"Found {len(cards)} cards to subscribe")
            
            for card in cards:
                try:
                    # Decrypt the card number
                    decrypted_card_number = decrypt_card_number(card.card_number) if card.card_number else None
                    
                    if not decrypted_card_number:
                        logger.warning(f"Skipping card {card.id} - No card number")
                        continue
                    
                    # Subscribe the card to PayPal
                    subscription = create_subscription(decrypted_card_number, card.expiry_date)
                    
                    if subscription and 'subscription_id' in subscription:
                        # Update the card with the subscription ID
                        card.subscription_id = subscription['subscription_id']
                        db.session.commit()
                        logger.info(f"Updated card {card.id} with subscription ID {subscription['subscription_id']}")
                    else:
                        logger.warning(f"Failed to subscribe card {card.id}")
                    
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error processing card {card.id}: {str(e)}")
            
            logger.info("Completed subscribing cards to PayPal")
            
        except Exception as e:
            logger.error(f"Error in subscribe_all_cards: {str(e)}")

def subscribe_card(card_id):
    """
    Subscribe a specific card to PayPal's Account Updater service
    
    Args:
        card_id: The ID of the card to subscribe
        
    Returns:
        dict: The subscription details or None if failed
    """
    app = create_app()
    with app.app_context():
        try:
            # Get the card
            card = Card.query.get(card_id)
            
            if not card:
                logger.error(f"Card {card_id} not found")
                return None
            
            # Decrypt the card number
            decrypted_card_number = decrypt_card_number(card.card_number) if card.card_number else None
            
            if not decrypted_card_number:
                logger.error(f"Card {card_id} has no card number")
                return None
            
            # Subscribe the card to PayPal
            subscription = create_subscription(decrypted_card_number, card.expiry_date)
            
            if subscription and 'subscription_id' in subscription:
                # Update the card with the subscription ID
                card.subscription_id = subscription['subscription_id']
                db.session.commit()
                logger.info(f"Updated card {card.id} with subscription ID {subscription['subscription_id']}")
                return subscription
            else:
                logger.error(f"Failed to subscribe card {card_id}")
                return None
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error subscribing card {card_id}: {str(e)}")
            return None

def update_card_from_webhook(subscription_id, new_expiry_date=None, new_card_number=None):
    """
    Update a card based on a webhook event from PayPal
    
    Args:
        subscription_id: The subscription ID of the card to update
        new_expiry_date: The new expiry date (optional)
        new_card_number: The new card number (optional)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Import the merchant_db_connector module
        from app.events.merchant_db_connector import update_card_by_subscription_id
        
        # Prepare the attributes to update
        attributes = {}
        if new_expiry_date:
            attributes['expiry_date'] = new_expiry_date
            logger.info(f"Updating expiry date for card with subscription ID {subscription_id}")
        
        if new_card_number:
            # In a real implementation, you would encrypt the new card number
            # For now, we'll just log that it would be updated
            logger.info(f"Would update card number for card with subscription ID {subscription_id}")
            # attributes['card_number'] = encrypt_card_number(new_card_number)
            # attributes['last_four'] = new_card_number[-4:]
        
        # Update the card using the merchant_db_connector
        if attributes:
            updated_card = update_card_by_subscription_id(subscription_id, attributes)
            if updated_card:
                logger.info(f"Successfully updated card with subscription ID {subscription_id}")
                return True
            else:
                logger.error(f"Failed to update card with subscription ID {subscription_id}")
                return False
        else:
            logger.warning(f"No attributes to update for card with subscription ID {subscription_id}")
            return True
            
    except Exception as e:
        logger.error(f"Error updating card with subscription ID {subscription_id}: {str(e)}")
        return False

if __name__ == "__main__":
    # If run directly, subscribe all cards
    subscribe_all_cards()
