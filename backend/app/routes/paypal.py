from flask import Blueprint, request, jsonify
from app import db
from sqlalchemy.exc import SQLAlchemyError
from app.events.card_subscription_manager import update_card_from_webhook, create_subscription
from app.utils.encryption import encrypt_card_number
import logging
import json

# Set up logging
logging.basicConfig(
    filename='paypal_webhook.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('paypal_routes')

paypal_bp = Blueprint('paypal', __name__)

@paypal_bp.route('/create_subscription', methods=['POST'])
def create_paypal_subscription():
    """
    Create a PayPal Account Updater subscription for a card
    """
    data = request.json
    pan = data.get('pan')
    expiry_date = data.get('expiry_date')
    
    if not pan or not expiry_date:
        return jsonify({"error": "Card number and expiry date are required"}), 400
    
    # Call the create_subscription function from card_subscription_manager
    subscription = create_subscription(pan, expiry_date)
    
    if not subscription:
        return jsonify({"error": "Failed to create subscription"}), 500
    
    return jsonify(subscription), 200

@paypal_bp.route('/webhook', methods=['POST'])
def paypal_webhook():
    """
    Handle webhook events from PayPal's Account Updater service
    """
    try:
        event_data = request.json
        logger.info(f"Received PayPal webhook: {json.dumps(event_data)}")
        
        event_type = event_data.get('event_type')
        
        if event_type == 'CARD_UPDATED':
            # Process card update event
            subscription_id = event_data.get('subscription_id')
            new_expiry_date = event_data.get('new_expiry_date')
            new_card_number = event_data.get('new_card_number')
            
            if not subscription_id:
                logger.error("Missing subscription_id in webhook event")
                return jsonify({"error": "Missing subscription_id"}), 400
            
            # Update the card in the database
            success = update_card_from_webhook(
                subscription_id=subscription_id,
                new_expiry_date=new_expiry_date,
                new_card_number=new_card_number
            )
            
            if success:
                logger.info(f"Successfully processed webhook for subscription {subscription_id}")
                return jsonify({"status": "success"}), 200
            else:
                logger.error(f"Failed to process webhook for subscription {subscription_id}")
                return jsonify({"error": "Failed to update card"}), 500
        else:
            logger.info(f"Ignoring webhook event of type {event_type}")
            return jsonify({"status": "ignored"}), 200
    
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({"error": str(e)}), 500
