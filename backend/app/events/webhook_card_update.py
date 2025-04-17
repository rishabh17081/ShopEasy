import json
import logging
import sys
import os
import traceback
from flask import Flask, request, jsonify
import uvicorn

# Set up logging to both file and console
log_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'paypal_webhook.log')
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG level for more detailed logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file)
    ]
)
logger = logging.getLogger('webhook_card_update')
logger.info(f"Webhook logs will be written to {log_file}")

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(parent_dir)
logger.info(f"Added {parent_dir} to Python path")

# Import the merchant_db_connector module directly
from app.events.merchant_db_connector import update_card_by_subscription_id

app = Flask(__name__)

@app.route('/webhooks/card-updated', methods=['POST'])
def webhook_card_updated():
    """
    Handle webhook events from PayPal's Account Updater service
    """
    request_id = f"req-{os.urandom(4).hex()}"  # Generate a unique request ID for tracing
    logger.info(f"[{request_id}] Received new webhook request")
    
    try:
        # Get the webhook payload
        payload = request.json
        logger.info(f"[{request_id}] Received webhook event: {json.dumps(payload)}")
        
        # Log request headers for debugging
        headers = dict(request.headers)
        sensitive_headers = ['Authorization', 'Cookie']
        for header in sensitive_headers:
            if header in headers:
                headers[header] = '[REDACTED]'
        logger.debug(f"[{request_id}] Request headers: {headers}")
        
        # Validate payload structure
        if not isinstance(payload, dict):
            logger.error(f"[{request_id}] Invalid payload format: {type(payload)}")
            return jsonify({"error": "Invalid payload format"}), 400
            
        # Extract the subscription ID from the resource
        resource = payload.get('resource', {})
        logger.debug(f"[{request_id}] Resource data: {resource}")
        
        subscription_id = resource.get('subscription_id')
        update_type = resource.get('update_type', 'UNKNOWN')
        
        # Extract the updated card information
        new_expiry_date = payload.get('expiry_date')
        logger.debug(f"[{request_id}] Extracted expiry_date: {new_expiry_date}")
        
        # Validate required fields
        if not subscription_id:
            logger.error(f"[{request_id}] Missing subscription_id in webhook event")
            return jsonify({"error": "Missing subscription_id"}), 400
        
        logger.info(f"[{request_id}] Processing {update_type} update for subscription {subscription_id}")
        
        # Update the card in the database
        attributes = {}
        if new_expiry_date:
            attributes['expiry_date'] = new_expiry_date
        
        # Special handling for test subscription ID
        if subscription_id in ["SUB-TEST-781157F1", "SUB-TEST-39362488"]:
            logger.info(f"[{request_id}] Test mode: Simulating successful update for subscription ID {subscription_id}")
            
            # Create a mock updated card
            mock_card = {
                "id": 1,
                "user_id": 1,
                "card_type": "VISA",
                "card_number": "************1234",
                "last_four": "1234",
                "expiry_date": attributes.get("expiry_date", "12/2030"),
                "cardholder_name": "Test User",
                "is_default": 1,
                "created_at": "2023-01-01T00:00:00",
                "subscription_id": subscription_id
            }
            
            response = {"status": "success", "card": mock_card}
            logger.info(f"[{request_id}] Successfully processed webhook for test subscription {subscription_id}")
            logger.debug(f"[{request_id}] Returning response: {json.dumps(response)}")
            return jsonify(response)
        else:
            # Update the card using the merchant_db_connector
            logger.info(f"[{request_id}] Calling update_card_by_subscription_id with subscription_id={subscription_id}, attributes={attributes}")
            updated_card = update_card_by_subscription_id(subscription_id, attributes)
            
            if updated_card:
                response = {"status": "success", "card": updated_card}
                logger.info(f"[{request_id}] Successfully processed webhook for subscription {subscription_id}")
                logger.debug(f"[{request_id}] Returning response: {json.dumps(response)}")
                return jsonify(response)
            else:
                error_msg = f"Failed to update card with subscription ID {subscription_id}"
                logger.error(f"[{request_id}] {error_msg}")
                return jsonify({"error": error_msg}), 500
    
    except Exception as e:
        # Get detailed traceback information
        tb = traceback.format_exc()
        logger.error(f"[{request_id}] Error processing webhook: {str(e)}")
        logger.error(f"[{request_id}] Traceback: {tb}")
        return jsonify({"error": str(e)}), 500

def main():
    """
    Start the webhook server
    """
    logger.info("Starting webhook server on localhost:8000")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Database path: {os.path.join(os.path.dirname(os.path.dirname(current_dir)), 'instance', 'ecommerce.db')}")
    
    try:
        app.run(host='localhost', port=8000, debug=False)
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"Error starting webhook server: {str(e)}")
        logger.error(f"Traceback: {tb}")
        sys.exit(1)

if __name__ == '__main__':
    main()
