import json
import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, Depends, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("webhook_notifications.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import the database connector function
import sys
import os

# Add the parent directory to the path to import the merchant_db_connector
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from merchant_db_connector import update_card_by_subscription_id

# Environment variables (in production, use proper environment variable handling)
WEBHOOK_SECRET = os.environ.get("PAYPAL_WEBHOOK_SECRET", "your_webhook_secret_here")

# Create FastAPI app
app = FastAPI(
    title="PayPal Card Update Webhook",
    description="Webhook endpoint for PayPal Account Updater service",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Webhook verification dependency
async def verify_webhook_signature(
    request: Request, 
    paypal_transmission_id: Optional[str] = Header(None, include_in_schema=False),
    paypal_transmission_time: Optional[str] = Header(None, include_in_schema=False),
    paypal_transmission_sig: Optional[str] = Header(None, include_in_schema=False),
    paypal_cert_url: Optional[str] = Header(None, include_in_schema=False),
    paypal_auth_algo: Optional[str] = Header(None, include_in_schema=False)
) -> bool:
    """
    Verify the PayPal webhook signature.
    
    In a production environment, you would implement proper signature verification
    using PayPal's SDK or verification methods.
    """
    # For development purposes, we'll skip actual verification
    # In production, implement proper signature verification using PayPal's SDK
    
    if all([paypal_transmission_id, paypal_transmission_time, paypal_transmission_sig]):
        print(f"PayPal Transmission ID: {paypal_transmission_id}")
        print(f"PayPal Transmission Time: {paypal_transmission_time}")
        print(f"PayPal Signature: {paypal_transmission_sig}")
        logger.info(f"PayPal Transmission ID: {paypal_transmission_id}")
        logger.info(f"PayPal Transmission Time: {paypal_transmission_time}")
    else:
        print("No PayPal signature headers found - continuing in development mode")
        logger.info("No PayPal signature headers found - continuing in development mode")
    
    # In a real implementation, you would verify the signature here
    return True

def parse_expiry_date(expiry_date: Optional[str]) -> tuple:
    """Parse expiry date in YYYY-MM format to month and year"""
    if not expiry_date:
        return None, None
    
    parts = expiry_date.split('-')
    if len(parts) != 2:
        print(f"Invalid expiry date format: {expiry_date}")
        return None, None
    
    print(f"Parsed expiry date: month={parts[1]}, year={parts[0]}")
    return parts[1], parts[0]  # month, year

def format_expiry_date(month: Optional[str], year: Optional[str]) -> Optional[str]:
    """Format expiry date as MM/YYYY"""
    if not month or not year:
        print(f"Missing month or year: month={month}, year={year}")
        return None
    
    # Ensure month is two digits
    month_str = str(month).zfill(2)
    
    # If year is provided as 2 digits, convert to 4 digits
    year_str = str(year)
    if len(year_str) == 2:
        year_str = f"20{year_str}"
        
    formatted_date = f"{month_str}/{year_str}"
    print(f"Formatted expiry date: {formatted_date}")
    return formatted_date

# Function to filter database-valid attributes
def filter_attributes_for_database(attributes: Dict[str, Any]) -> Dict[str, Any]:
    """
    Creates a copy of attributes with only the fields that can be stored in the database.
    Removes metadata fields that would cause validation errors.
    """
    # Define the valid fields for database update
    valid_db_fields = ['card_type', 'last_four', 'expiry_date', 'cardholder_name', 'subscription_id', 'is_default']
    
    # Create a new dictionary with only the valid fields
    filtered_attributes = {}
    for key, value in attributes.items():
        if key in valid_db_fields:
            filtered_attributes[key] = value
    
    print(f"Original attributes: {attributes}")
    print(f"Filtered attributes for DB: {filtered_attributes}")
    return filtered_attributes

# Support both the original endpoint from on_pp_card_update.py and the new one
@app.post("/webhooks/card-updated")
@app.post("/paypal-webhooks")
async def handle_paypal_webhook(
    request: Request,
    is_verified: bool = Depends(verify_webhook_signature)
):
    """
    Handle incoming PayPal Account Updater webhooks
    Compatible with both the old and new payload formats
    """
    try:
        # Parse the request body
        payload = await request.json()
        
        # Log the incoming webhook
        print(f"Received webhook payload: {json.dumps(payload)}")
        logger.info(f"Received webhook: {json.dumps(payload)}")
        
        # Verify the webhook signature (in production, properly check is_verified)
        if not is_verified and os.environ.get("ENVIRONMENT") == "production":
            print("Invalid webhook signature")
            logger.error("Invalid webhook signature")
            return JSONResponse(
                status_code=401,
                content={"status": "error", "message": "Invalid signature"}
            )
        
        # Validate the event type - we're flexible with both formats
        event_type = payload.get('event_type')
        print(f"Event type: {event_type}")
        if event_type not in ['CARD.UPDATED', 'PAYMENT.CARD-UPDATE']:
            print(f"Ignoring non-card-update event: {event_type}")
            logger.warning(f"Ignoring non-card-update event: {event_type}")
            return {"status": "ignored", "reason": "Not a card update event"}
        
        # Extract resource from payload
        resource = payload.get('resource', {})
        print(f"Resource data: {json.dumps(resource)}")
        
        # Extract subscription ID
        subscription_id = resource.get('subscription_id')
        print(f"Subscription ID: {subscription_id}")
        if not subscription_id:
            print("Missing subscription_id in webhook payload")
            logger.error("Missing subscription_id in webhook payload")
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Missing subscription_id"}
            )
        
        # Determine how to extract card details based on payload format
        updated_attributes = {}
        
        # Check if the payload has expiry_date at the top level (old format)
        if 'expiry_date' in payload:
            print(f"Found expiry_date in old format: {payload.get('expiry_date')}")
            month, year = parse_expiry_date(payload.get('expiry_date'))
            updated_attributes["expiry_date"] = format_expiry_date(month, year)
        
        # If resource has card_details, use those (new format)
        elif 'card_details' in resource and resource['card_details']:
            card_data = resource['card_details']
            print(f"Found card_details in new format: {json.dumps(card_data)}")
            # Extract details depending on the structure
            if isinstance(card_data, dict):
                if 'last_four' in card_data:
                    updated_attributes["last_four"] = card_data.get('last_four')
                    print(f"Extracted last_four: {card_data.get('last_four')}")
                
                if 'expiry_month' in card_data and 'expiry_year' in card_data:
                    updated_attributes["expiry_date"] = format_expiry_date(
                        card_data.get('expiry_month'), 
                        card_data.get('expiry_year')
                    )
                    print(f"Extracted and formatted expiry_date: {updated_attributes.get('expiry_date')}")
                
                if 'brand' in card_data:
                    updated_attributes["card_type"] = card_data.get('brand')
                    print(f"Extracted card_type: {card_data.get('brand')}")
        
        # Filter out None values
        updated_attributes = {k: v for k, v in updated_attributes.items() if v is not None}
        print(f"Final updated attributes before filtering: {updated_attributes}")
        
        if not updated_attributes:
            print(f"No valid card updates found for subscription {subscription_id}")
            logger.warning(f"No valid card updates found for subscription {subscription_id}")
            return {"status": "ignored", "reason": "No valid updates"}
        
        # Only keep attributes that are valid for database storage, filtering out metadata
        db_attributes = filter_attributes_for_database(updated_attributes)
        
        # Update the card in the database
        print(f"Updating card with subscription ID {subscription_id}: {db_attributes}")
        logger.info(f"Updating card with subscription ID {subscription_id}: {db_attributes}")
        update_result = update_card_by_subscription_id(subscription_id, db_attributes)
        
        print(f"Update result: {update_result}")
        if update_result.get("success"):
            print(f"Successfully updated card for subscription {subscription_id}")
            logger.info(f"Successfully updated card for subscription {subscription_id}")
            return {"status": "success", "message": "Card updated successfully"}
        else:
            error_message = update_result.get("error", "Unknown error")
            print(f"Failed to update card: {error_message}")
            logger.error(f"Failed to update card: {error_message}")
            return JSONResponse(
                status_code=500,
                content={"status": "error", "message": error_message}
            )
            
    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        logger.exception(f"Error processing webhook: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    print("Health check endpoint called")
    return {"status": "healthy", "service": "PayPal Card Update Webhook"}

# Default route
@app.get("/")
async def root():
    print("Root endpoint called")
    return {
        "service": "PayPal Card Update Webhook",
        "version": "1.0.0",
        "endpoints": [
            {"path": "/webhooks/card-updated", "method": "POST", "description": "Handle PayPal card update webhooks (original format)"},
            {"path": "/paypal-webhooks", "method": "POST", "description": "Handle PayPal card update webhooks (new format)"},
            {"path": "/health", "method": "GET", "description": "Health check endpoint"}
        ]
    }

# Main entry point for Uvicorn
if __name__ == "__main__":
    # For local development
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"Starting webhook server on {host}:{port}")
    # Run the FastAPI app with Uvicorn
    uvicorn.run(
        "webhook_card_update:app", 
        host=host, 
        port=port, 
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )