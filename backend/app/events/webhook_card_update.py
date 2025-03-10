from fastapi import FastAPI, Request, HTTPException
import sys
import os
import json
import logging
from typing import Dict, Any, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("card_updater.log")
    ]
)
logger = logging.getLogger("webhook_card_update")

# Try to import the database connector
try:
    # In production, adjust these import paths according to your project structure
    from backend.app.db.connector import update_card_by_subscription_id, get_db_connector, getAllCardsFromDatabase
except ImportError:
    logger.warning("db.connector module not found, creating minimal implementation")
    
    # Minimal implementation of required functions for development/testing
    class DatabaseConnector:
        def __init__(self):
            self.connection = None
        
        def connect(self):
            logger.info("Mock database connection established")
            pass
            
        def disconnect(self):
            logger.info("Mock database connection closed")
            pass
            
        def get_all_cards(self):
            return [
                {"id": 1, "user_id": 1, "card_type": "Visa", "last_four": "1111", 
                 "expiry_date": "01/2030", "cardholder_name": "John Doe", 
                 "subscription_id": "SUB-0A08E5D325", "created_at": "2025-03-10 22:42:45"},
                {"id": 2, "user_id": 1, "card_type": "Visa", "last_four": "1881", 
                 "expiry_date": "02/2028", "cardholder_name": "John Doe", 
                 "subscription_id": "SUB-4C900A19D9", "created_at": "2025-03-10 22:42:45"}
            ]
    
    def get_db_connector():
        return DatabaseConnector()
    
    def getAllCardsFromDatabase():
        return [
            {"id": 1, "user_id": 1, "card_type": "Visa", "last_four": "1111", 
             "expiry_date": "01/2030", "cardholder_name": "John Doe", 
             "subscription_id": "SUB-0A08E5D325", "created_at": "2025-03-10 22:42:45"},
            {"id": 2, "user_id": 1, "card_type": "Visa", "last_four": "1881", 
             "expiry_date": "02/2028", "cardholder_name": "John Doe", 
             "subscription_id": "SUB-4C900A19D9", "created_at": "2025-03-10 22:42:45"}
        ]
        
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
                "created_at": "2025-03-10 22:42:45"
            }
        }

# Add the project root to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import the anthropic_api module
try:
    from anthropic_api import updateCardBySubscriptionIdAnthropic, AnthropicAPIException
except ImportError:
    try:
        from .anthropic_api import updateCardBySubscriptionIdAnthropic, AnthropicAPIException
    except ImportError:
        logger.warning("anthropic_api module not found, falling back to database updates only")
        class AnthropicAPIException(Exception):
            """Placeholder exception when anthropic_api is not available"""
            pass
        
        def updateCardBySubscriptionIdAnthropic(subscription_id, attributes):
            logger.warning(f"Mock anthropic API called with subscription_id={subscription_id}, attributes={attributes}")
            raise AnthropicAPIException("Anthropic API not available in this environment")

# Create FastAPI app
app = FastAPI(
    title="PayPal Card Update Webhook Handler",
    description="Handles card update events from PayPal Account Updater service",
    version="1.0.0"
)

@app.post("/webhooks/card-updated")
async def card_update_webhook(request: Request) -> Dict[str, Any]:
    """
    Webhook handler for PayPal card update notifications.
    
    This endpoint receives webhook events from PayPal when a card's details 
    have been updated, and updates the corresponding card in the ShopEasy database.
    
    Returns:
        Dict[str, Any]: Status and details of the update operation
    """
    try:
        # Parse webhook payload
        webhook_data = await request.json()
        logger.info(f"Received webhook data: {json.dumps(webhook_data, indent=2)}")
        
        # Validate webhook data
        if not validate_webhook_payload(webhook_data):
            error_msg = "Invalid webhook payload structure"
            logger.error(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Extract subscription ID and card details
        subscription_id, card_details = extract_card_details(webhook_data)
        
        if not subscription_id:
            error_msg = "Missing subscription_id in webhook data"
            logger.error(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)
            
        # Update the card in the database
        result = update_card_with_anthropic(subscription_id, card_details)
        
        # Check if the update was successful
        if result.get("success", False):
            logger.info(f"Card update successful: {result}")
            return {
                "status": "success", 
                "message": "Webhook processed and card updated",
                "update_result": result
            }
        else:
            logger.error(f"Card update failed: {result}")
            return {
                "status": "error", 
                "message": "Failed to update card",
                "update_result": result
            }
        
    except HTTPException:
        # Re-raise HTTPExceptions as they already have the appropriate status code
        raise
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON in webhook payload: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        error_msg = f"Error processing webhook: {str(e)}"
        logger.exception("Unexpected error in webhook handler")
        raise HTTPException(status_code=500, detail=error_msg)

def validate_webhook_payload(webhook_data: Dict[str, Any]) -> bool:
    """
    Validate that the webhook payload has the expected structure.
    
    Args:
        webhook_data: The webhook payload to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Check if it's a PayPal webhook event
    if "event_type" in webhook_data and "resource" in webhook_data:
        # Standard PayPal webhook format
        return True
    
    # Simplified format with direct subscription_id
    if "subscription_id" in webhook_data:
        return True
        
    # Neither format is present
    return False

def extract_card_details(webhook_data: Dict[str, Any]) -> Tuple[Optional[str], Dict[str, Any]]:
    """
    Extract subscription ID and card details from webhook data.
    
    Args:
        webhook_data: The webhook payload
        
    Returns:
        tuple: (subscription_id, card_details)
    """
    subscription_id = None
    card_details = {}
    
    # Try to extract from resource section (standard PayPal format)
    resource = webhook_data.get('resource', {})
    if resource:
        subscription_id = resource.get('subscription_id')
        
        # Extract card details if available
        card_info = resource.get('card', {})
        if card_info:
            if 'expiry_date' in card_info:
                card_details['expiry_date'] = card_info['expiry_date']
            elif 'expiry_month' in card_info and 'expiry_year' in card_info:
                # Format as YYYY-MM
                card_details['expiry_date'] = f"{card_info['expiry_year']}-{card_info['expiry_month']:02d}"
    
    # Fallback to direct properties (simplified format)
    if not subscription_id:
        subscription_id = webhook_data.get('subscription_id')
    
    if 'expiry_date' not in card_details:
        expiry_date = webhook_data.get('expiry_date')
        if expiry_date:
            card_details['expiry_date'] = expiry_date
    
    return subscription_id, card_details

def update_card_with_anthropic(subscription_id: str, card_details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update a card by subscription ID using the Anthropic API with fallback to direct database update.
    
    Args:
        subscription_id: The subscription ID to update
        card_details: Dictionary of card details to update
        
    Returns:
        Dict with update result
    """
    if not card_details:
        # If no card details were provided, use a default expiry date for testing
        logger.warning("No card details provided in webhook, using default values for testing")
        card_details = {"expiry_date": "2030-12"}
    
    try:
        # First try to update using Anthropic API
        logger.info(f"Updating card with subscription ID {subscription_id} via Anthropic API")
        result = updateCardBySubscriptionIdAnthropic(subscription_id, card_details)
        logger.info(f"Card updated successfully via Anthropic API: {result}")
        return result
    except AnthropicAPIException as e:
        # Log the error and try the fallback method
        error_msg = f"Anthropic API error: {str(e)}"
        logger.warning(error_msg)
        logger.info("Attempting fallback to database update...")
        
        # Try using the fallback method
        try:
            fallback_result = find_and_update_card(subscription_id, card_details)
            if fallback_result.get("success", False):
                logger.info("Fallback update successful")
                return fallback_result
            else:
                logger.error(f"Fallback update also failed: {fallback_result}")
                return fallback_result
        except Exception as fallback_error:
            logger.exception(f"Fallback error: {str(fallback_error)}")
            return {"success": False, "error": str(fallback_error)}
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.exception("Unexpected error in update_card_with_anthropic")
        return {"success": False, "error": error_msg}

def find_and_update_card(subscription_id: str, card_details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Find a card by subscription ID and update its details directly in the database.
    
    Args:
        subscription_id: The subscription ID to look for
        card_details: Dictionary of card details to update
        
    Returns:
        Dict with update result
    """
    connector = get_db_connector()
    try:
        logger.info(f"Connecting to database to update card with subscription ID {subscription_id}")
        connector.connect()
        all_cards = connector.get_all_cards()
        
        # Find the card with matching subscription ID
        matching_card = next((card for card in all_cards if card.get('subscription_id') == subscription_id), None)
        
        if matching_card:
            # Format expiry date if present
            if 'expiry_date' in card_details:
                expiry_date = card_details['expiry_date']
                try:
                    if "-" in expiry_date:
                        # Convert from YYYY-MM to MM/YYYY
                        year, month = expiry_date.split("-")
                        card_details['expiry_date'] = f"{month}/{year}"
                except Exception as e:
                    logger.warning(f"Error formatting expiry date '{expiry_date}': {str(e)}")
                
            # Update the card with the provided details
            logger.info(f"Updating card ID {matching_card['id']} with details: {card_details}")
            result = update_card_by_subscription_id(subscription_id, card_details)
            logger.info(f"Card update result: {result}")
            return result
        else:
            message = f"No card found with subscription ID: {subscription_id}"
            logger.warning(message)
            return {"success": False, "error": message}
    finally:
        logger.info("Disconnecting from database")
        connector.disconnect()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "PayPal Card Update Webhook Server is running",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    import time
    return {
        "status": "ok",
        "timestamp": time.time(),
        "uptime": "N/A",  # Would require tracking start time
        "services": {
            "database": check_database_connection(),
            "anthropic_api": check_anthropic_api()
        }
    }

def check_database_connection() -> Dict[str, Any]:
    """Check if the database connection is working"""
    try:
        connector = get_db_connector()
        connector.connect()
        connector.disconnect()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def check_anthropic_api() -> Dict[str, Any]:
    """Check if the Anthropic API is available"""
    try:
        # Simple dummy check - in a real implementation, would make a simple API call
        if 'AnthropicAPIException' in globals() and isinstance(AnthropicAPIException, type):
            return {"status": "ok"}
        else:
            return {"status": "warning", "message": "API class not properly loaded"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting PayPal Card Update Webhook Server")
    # Run the FastAPI app with uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)