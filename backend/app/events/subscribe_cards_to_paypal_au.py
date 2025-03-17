import logging
import sys
import os
import json
from datetime import datetime
from flask import Flask

# Add the parent directory to the path to import the app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from app import db, create_app

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='paypal_subscription.log'
)
logger = logging.getLogger(__name__)

def create_paypal_subscription(card_number, expiry_date):
    """
    Create a subscription in PayPal Account Updater for a card.
    
    Args:
        card_number (str): The card number (PAN)
        expiry_date (str): The expiry date in YYYY-MM format
    
    Returns:
        dict: The created subscription details or None if creation failed
    """
    try:
        # In a real implementation, this would make an API call to PayPal
        # For this example, we'll simulate a successful response
        
        # Log the request (mask the card number for security)
        masked_card = f"{'*' * (len(card_number) - 4)}{card_number[-4:]}"
        logger.info(f"Creating PayPal AU subscription for card: {masked_card}, expiry: {expiry_date}")
        
        # Generate a fake subscription ID
        import uuid
        subscription_id = f"SUB-{uuid.uuid4().hex[:12].upper()}"
        
        # Simulate a successful response
        response = {
            "id": subscription_id,
            "status": "ACTIVE",
            "create_time": datetime.utcnow().isoformat(),
            "card_details": {
                "last_four": card_number[-4:],
                "expiry_date": expiry_date
            }
        }
        
        logger.info(f"Successfully created PayPal AU subscription: {subscription_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error creating PayPal AU subscription: {str(e)}")
        return None

def subscribe_all_cards():
    """
    Subscribe all cards in the database to PayPal Account Updater.
    
    Returns:
        dict: A summary of the subscription process
    """
    try:
        # Get all cards that don't have a subscription_id yet
        cursor = db.session.execute(
            """
            SELECT id, card_type, card_number, last_four, expiry_date, cardholder_name, 
                   is_default, subscription_id
            FROM cards 
            WHERE subscription_id IS NULL
            """
        )
        
        cards = [dict(row) for row in cursor]
        logger.info(f"Found {len(cards)} cards without PayPal AU subscriptions")
        
        results = {
            "total": len(cards),
            "success": 0,
            "failed": 0,
            "details": []
        }
        
        for card in cards:
            try:
                # Skip cards without a card number (shouldn't happen in a real system)
                if not card.get('card_number'):
                    logger.warning(f"Skipping card ID {card['id']} - missing card number")
                    results["failed"] += 1
                    results["details"].append({
                        "card_id": card['id'],
                        "status": "skipped",
                        "reason": "Missing card number"
                    })
                    continue
                
                # Convert MM/YYYY format to YYYY-MM format for PayPal
                expiry_date = card.get('expiry_date')
                if '/' in expiry_date:
                    month, year = expiry_date.split('/')
                    # Handle 2-digit years
                    if len(year) == 2:
                        year = f"20{year}"
                    expiry_date_paypal = f"{year}-{month}"
                else:
                    expiry_date_paypal = expiry_date
                
                # Create a subscription in PayPal AU
                subscription = create_paypal_subscription(card['card_number'], expiry_date_paypal)
                
                if subscription and 'id' in subscription:
                    subscription_id = subscription['id']
                    
                    # Update the card with the subscription ID
                    db.session.execute(
                        "UPDATE cards SET subscription_id = :subscription_id WHERE id = :card_id",
                        {"subscription_id": subscription_id, "card_id": card['id']}
                    )
                    
                    logger.info(f"Updated card ID {card['id']} with subscription ID: {subscription_id}")
                    results["success"] += 1
                    results["details"].append({
                        "card_id": card['id'],
                        "status": "success",
                        "subscription_id": subscription_id
                    })
                else:
                    logger.warning(f"Failed to create PayPal AU subscription for card ID {card['id']}")
                    results["failed"] += 1
                    results["details"].append({
                        "card_id": card['id'],
                        "status": "failed",
                        "reason": "Subscription creation failed"
                    })
            except Exception as e:
                logger.error(f"Error processing card ID {card['id']}: {str(e)}")
                results["failed"] += 1
                results["details"].append({
                    "card_id": card['id'],
                    "status": "error",
                    "reason": str(e)
                })
        
        # Commit all changes
        db.session.commit()
        logger.info(f"Subscription process completed: {results['success']} succeeded, {results['failed']} failed")
        return results
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error subscribing cards to PayPal AU: {str(e)}")
        return {
            "total": 0,
            "success": 0,
            "failed": 0,
            "error": str(e)
        }

def main():
    """
    Main function to subscribe all cards to PayPal Account Updater.
    """
    try:
        logger.info("Starting PayPal AU subscription process for all cards")
        
        # Create and use a Flask application context
        app = create_app()
        with app.app_context():
            results = subscribe_all_cards()
            logger.info(f"Subscription process summary: {json.dumps(results, indent=2)}")
    except Exception as e:
        logger.error(f"Unexpected error in main function: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
