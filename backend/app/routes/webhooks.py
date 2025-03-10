from flask import Blueprint, request, jsonify, current_app
import logging
import json
from app.events.paypal_webhook import process_webhook_event, verify_webhook_signature

# Create blueprint
webhooks_bp = Blueprint('webhooks', __name__)

# Set up logging
logger = logging.getLogger(__name__)

@webhooks_bp.route('/paypal/account-updater', methods=['POST'])
def paypal_account_updater_webhook():
    """
    Handle PayPal Account Updater webhook events.
    
    This endpoint receives notifications when card information is updated through
    PayPal's Account Updater service, such as when a card's expiry date changes.
    """
    try:
        # Get webhook payload and headers
        webhook_payload = request.get_data()
        signature_header = request.headers.get('PayPal-Signature')
        
        # Get webhook secret from environment
        webhook_secret = current_app.config.get('PAYPAL_WEBHOOK_SECRET')
        
        # Skip signature verification in development mode
        if current_app.config.get('FLASK_ENV') == 'development' and current_app.config.get('SKIP_WEBHOOK_VERIFICATION'):
            logger.warning("SKIPPING WEBHOOK SIGNATURE VERIFICATION IN DEVELOPMENT MODE")
            is_valid = True
        else:
            # Verify webhook signature
            is_valid = verify_webhook_signature(webhook_payload, signature_header, webhook_secret)
        
        if not is_valid:
            logger.error("Invalid webhook signature")
            return jsonify({
                'success': False,
                'error': 'Invalid webhook signature'
            }), 401
        
        # Parse webhook payload
        event_data = json.loads(webhook_payload)
        
        # Process the webhook event
        success, message = process_webhook_event(event_data)
        
        if success:
            logger.info(f"Successfully processed webhook: {message}")
            return jsonify({
                'success': True,
                'message': message
            }), 200
        else:
            logger.error(f"Failed to process webhook: {message}")
            return jsonify({
                'success': False,
                'error': message
            }), 400
            
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Error processing webhook: {str(e)}"
        }), 500
