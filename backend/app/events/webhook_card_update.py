from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
import json
import logging
import hmac
import hashlib
import base64
import os
from typing import Dict, Any, Optional
from datetime import datetime
import httpx
from pydantic import BaseModel

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configuration - In production, these should come from environment variables
PAYPAL_WEBHOOK_ID = os.getenv("PAYPAL_WEBHOOK_ID", "default-webhook-id")
PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID", "default-client-id")
PAYPAL_SECRET = os.getenv("PAYPAL_SECRET", "default-secret")

# Models
class CardUpdateEvent(BaseModel):
    event_type: str
    resource: Dict[str, Any]
    summary: str
    create_time: datetime
    resource_type: str
    resource_version: str
    event_version: str
    resource_id: Optional[str] = None

# Database operation functions
async def update_card_in_database(subscription_id: str, card_details: Dict[str, Any]) -> bool:
    """
    Update card details in the database based on subscription ID
    
    Args:
        subscription_id: The PayPal subscription ID
        card_details: Updated card details
        
    Returns:
        bool: Success status
    """
    try:
        # In production, replace with actual database operations
        logger.info(f"Updating database with subscription ID: {subscription_id}")
        logger.info(f"New card details: {json.dumps(card_details, default=str)}")
        
        # Mock successful update - replace with actual DB call
        # Example of how you might use the function from your database:
        # from your_db_module import update_card_by_subscription_id
        # result = await update_card_by_subscription_id(subscription_id, card_details)
        
        return True
    except Exception as e:
        logger.error(f"Database update error: {str(e)}")
        return False

# Webhook verification
async def verify_webhook_signature(request: Request, payload: bytes) -> bool:
    """
    Verify that the webhook request is genuinely from PayPal
    
    Args:
        request: FastAPI request object
        payload: Raw request payload
        
    Returns:
        bool: True if signature is valid
    """
    try:
        # Get PayPal-Signature header
        paypal_sig = request.headers.get("PayPal-Signature")
        if not paypal_sig:
            logger.warning("No PayPal-Signature header found")
            return False
            
        # Parse signature header
        sig_dict = {}
        for key_value in paypal_sig.split(","):
            if "=" in key_value:
                k, v = key_value.split("=", 1)
                sig_dict[k.strip()] = v.strip()
        
        # Check if required fields are present
        if not all(k in sig_dict for k in ["t", "v1"]):
            logger.warning("Missing required signature components")
            return False
            
        # Get timestamp and signature from header
        timestamp = sig_dict["t"]
        actual_sig = sig_dict["v1"]
        
        # Calculate expected signature
        data_to_sign = timestamp + "." + payload.decode("utf-8")
        h = hmac.new(
            PAYPAL_WEBHOOK_ID.encode("utf-8"), 
            data_to_sign.encode("utf-8"),
            hashlib.sha256
        )
        expected_sig = base64.b64encode(h.digest()).decode("ascii")
        
        # Compare signatures
        return hmac.compare_digest(actual_sig, expected_sig)
    except Exception as e:
        logger.error(f"Signature verification error: {str(e)}")
        return False

# Routes
@app.post("/webhook/paypal/card-update")
async def handle_paypal_webhook(request: Request):
    """Endpoint to receive PayPal card update events"""
    # Get raw payload for signature verification
    payload = await request.body()
    
    # Verify webhook signature in production
    # if not await verify_webhook_signature(request, payload):
    #     logger.warning("Invalid webhook signature")
    #     raise HTTPException(status_code=401, detail="Invalid signature")
    
    try:
        # Parse payload
        event_data = json.loads(payload)
        logger.info(f"Received webhook event: {event_data.get('event_type', 'unknown')}")
        
        # Check if this is a card update event
        if event_data.get("event_type") != "PAYMENT.CARD.ACCOUNT-STATUS.UPDATED":
            logger.info(f"Ignoring non-card-update event: {event_data.get('event_type')}")
            return JSONResponse(content={"status": "ignored"})
        
        # Extract relevant card details
        resource = event_data.get("resource", {})
        subscription_id = resource.get("id")
        
        if not subscription_id:
            logger.error("Missing subscription ID in event payload")
            raise HTTPException(status_code=400, detail="Missing subscription ID")
        
        # Map to card fields we need to update in our database
        card_update = {
            "card_status": resource.get("account_status", "UNKNOWN"),
            "last_updated": datetime.now().isoformat(),
            "card_brand": resource.get("card_type"),
            "last_four": resource.get("last_digits"),
            "expiry_month": resource.get("expiry_month"),
            "expiry_year": resource.get("expiry_year")
        }
        
        # Update database with new card details
        success = await update_card_in_database(subscription_id, card_update)
        
        if success:
            logger.info(f"Successfully processed card update for subscription {subscription_id}")
            return JSONResponse(content={"status": "success"})
        else:
            logger.error(f"Failed to update database for subscription {subscription_id}")
            raise HTTPException(status_code=500, detail="Database update failed")
            
    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook payload")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint for the webhook service"""
    return {"status": "healthy", "service": "PayPal Card Update Webhook"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
