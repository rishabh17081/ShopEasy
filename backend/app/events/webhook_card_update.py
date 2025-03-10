from fastapi import FastAPI, Request
import sys
import os
import json
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Try to import database connector modules
try:
    from merchant_connector.merchant_db_connector import updateCardAttributes, update_card_by_subscription_id, get_db_connector, getAllCardsFromDatabase
except ImportError:
    logger.warning("merchant_db_connector module not found, creating minimal implementation")
    
    # Minimal implementation of required functions
    class DatabaseConnector:
        def __init__(self):
            self.connection = None
        
        def connect(self):
            logger.info("Mock database connection established")
            return True
            
        def disconnect(self):
            logger.info("Mock database connection closed")
            return True
            
        def get_all_cards(self):
            return getAllCardsFromDatabase()
    
    def get_db_connector():
        return DatabaseConnector()
        
    def updateCardAttributes(card_id, attributes):
        logger.info(f"Mock updateCardAttributes called with card_id={card_id}, attributes={attributes}")
        return {
            "success": True,
            "message": f"Card with ID {card_id} updated successfully (mock)",
            "card": {
                "id": card_id,
                "user_id": 1,
                "card_type": "Visa",
                "last_four": "1111",
                "expiry_date": attributes.get("expiry_date", "12/2025"),
                "cardholder_name": "John Doe",
                "subscription_id": "SUB-7D80F0A048",
                "created_at": "2024-01-01 00:00:00"
            }
        }
    
    def update_card_by_subscription_id(subscription_id, attributes):
        logger.info(f"Mock update_card_by_subscription_id called with subscription_id={subscription_id}, attributes={attributes}")
        return {
            "success": True,
            "message": f"Card with subscription ID {subscription_id} updated successfully (mock)",
            "card": {
                "id": 1,
                "user_id": 1,
                "card_type": "Visa",
                "last_four": "1111",
                "expiry_date": attributes.get("expiry_date", "12/2025"),
                "cardholder_name": "John Doe",
                "subscription_id": subscription_id,
                "created_at": "2024-01-01 00:00:00"
            }
        }
    
    def getAllCardsFromDatabase():
        logger.info("Mock getAllCardsFromDatabase called")
        return []

# Create FastAPI app
app = FastAPI()

@app.post("/webhooks/card-updated")
async def card_update_webhook(request: Request):
    """Webhook handler for card update notifications from PayPal Account Updater"""
    try:
        # Parse webhook payload
        webhook_data = await request.json()
        logger.info(f"Received webhook data: {json.dumps(webhook_data)}")
        
        # Extract subscription ID from the resource section
        subscription_id = None
        resource = webhook_data.get('resource', {})
        if resource:
            subscription_id = resource.get('subscription_id')
        
        # For testing purposes, also look at the root level
        if not subscription_id:
            subscription_id = webhook_data.get('subscription_id')
        
        if not subscription_id:
            return {"status": "error", "message": "Missing subscription_id in webhook data"}
        
        # Extract updated details - in a production scenario, these would come from the webhook
        updated_details = resource.get('updated_details', {})
        if not updated_details and webhook_data.get('expiry_date'):
            # For testing, use root level fields if resource structure is missing
            updated_details = {
                'expiry_date': webhook_data.get('expiry_date')
            }
        
        # Extract expiry date and other card details
        new_expiry_date = updated_details.get('expiry_date')
        card_type = updated_details.get('card_type')
        last_four = updated_details.get('last_four')
        
        # Prepare update data
        update_data = {}
        if new_expiry_date:
            # Format date from YYYY-MM to MM/YYYY if needed
            try:
                if "-" in new_expiry_date:
                    year, month = new_expiry_date.split("-")
                    update_data['expiry_date'] = f"{month}/{year}"
                else:
                    update_data['expiry_date'] = new_expiry_date
            except Exception as e:
                logger.error(f"Error formatting expiry date: {str(e)}")
                update_data['expiry_date'] = new_expiry_date
        
        if card_type:
            update_data['card_type'] = card_type
            
        if last_four:
            update_data['last_four'] = last_four
            
        # Use the update_card_with_subscription function to update the card
        result = update_card_with_subscription(subscription_id, update_data)
        
        # Check if the update was successful
        if result.get("success", False):
            return {
                "status": "success", 
                "message": "Webhook processed and card updated",
                "update_result": result
            }
        else:
            return {
                "status": "error", 
                "message": "Failed to update card",
                "update_result": result
            }
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return {"status": "error", "message": f"Error processing webhook: {str(e)}"}

def update_card_with_subscription(subscription_id, update_data):
    """
    Update a card by subscription ID.
    
    Args:
        subscription_id: The subscription ID to update
        update_data: The data to update
        
    Returns:
        Dict with update result
    """
    try:
        # Try to update the card directly with the subscription ID
        result = update_card_by_subscription_id(subscription_id, update_data)
        logger.info(f"Card updated successfully: {result}")
        return result
    except Exception as e:
        error_msg = f"Error updating card: {str(e)}"
        logger.error(error_msg)
        logger.info("Attempting fallback to database search...")
        
        # Try using the fallback method to find the card by subscription ID
        try:
            fallback_result = find_and_update_card(subscription_id, update_data)
            if fallback_result.get("success", False):
                logger.info("Fallback update successful")
                return fallback_result
            else:
                logger.error(f"Fallback update also failed: {fallback_result}")
        except Exception as fallback_error:
            logger.error(f"Fallback error: {str(fallback_error)}")
        
        # Return the original error if fallback also fails
        return {"success": False, "error": error_msg}

def find_and_update_card(subscription_id, update_data):
    """
    Find a card by subscription ID and update its details.
    
    Args:
        subscription_id: The subscription ID to look for
        update_data: The data to update
        
    Returns:
        Dict with update result
    """
    connector = get_db_connector()
    try:
        connector.connect()
        all_cards = connector.get_all_cards()
        
        # Find the card with matching subscription ID
        matching_card = next((card for card in all_cards if card['subscription_id'] == subscription_id), None)
        
        if matching_card:
            # Update the card with the new details
            result = updateCardAttributes(matching_card['id'], update_data)
            logger.info(f"Card update result: {result}")
            return result
        else:
            message = f"No card found with subscription ID: {subscription_id}"
            logger.warning(message)
            return {"success": False, "error": message}
    finally:
        connector.disconnect()

# Add this for testing the endpoint
@app.get("/")
async def root():
    return {"message": "Card Update Webhook Server is running"}

if __name__ == "__main__":
    import uvicorn
    # Run the FastAPI app with uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)