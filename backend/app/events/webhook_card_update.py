from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
import json
import logging
import hmac
import hashlib
import base64
import os
from typing import Dict, Any
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("webhook_card_update")

# Create router
router = APIRouter()

# PayPal webhook secret - In production, store this in environment variables
WEBHOOK_SECRET = os.getenv("PAYPAL_WEBHOOK_SECRET", "your-webhook-secret")

async def verify_webhook_signature(request: Request) -> bool:
    """
    Verify that the webhook request is coming from PayPal by validating the signature.
    
    Args:
        request: The incoming webhook request
        
    Returns:
        bool: True if signature is valid, False otherwise
    """
    try:
        # Get PayPal signature from header
        paypal_signature = request.headers.get("PAYPAL-TRANSMISSION-SIG")
        paypal_cert_url = request.headers.get("PAYPAL-CERT-URL")
        paypal_transmission_id = request.headers.get("PAYPAL-TRANSMISSION-ID")
        paypal_transmission_time = request.headers.get("PAYPAL-TRANSMISSION-TIME")
        
        if not all([paypal_signature, paypal_cert_url, paypal_transmission_id, paypal_transmission_time]):
            logger.error("Missing required PayPal signature headers")
            return False
        
        # Get request body
        body = await request.body()
        
        # Create the validation string
        validation_string = f"{paypal_transmission_id}|{paypal_transmission_time}|{body.decode('utf-8')}"
        
        # Generate signature using HMAC with SHA256
        hmac_obj = hmac.new(
            WEBHOOK_SECRET.encode('utf-8'),
            validation_string.encode('utf-8'),
            hashlib.sha256
        )
        
        signature = base64.b64encode(hmac_obj.digest()).decode('utf-8')
        
        # Compare signatures
        return hmac.compare_digest(signature, paypal_signature)
    except Exception as e:
        logger.error(f"Signature verification error: {str(e)}")
        return False

async def update_card_in_database(event_data: Dict[str, Any]) -> bool:
    """
    Update card information in database based on webhook event.
    
    Args:
        event_data: The webhook event data containing updated card information
        
    Returns:
        bool: True if database update is successful, False otherwise
    """
    try:
        # Extract necessary information from event
        resource = event_data.get("resource", {})
        subscription_id = resource.get("id")
        
        if not subscription_id:
            logger.error("Missing subscription ID in event data")
            return False
        
        # Get updated card details
        updated_card_data = resource.get("account_status", {})
        if not updated_card_data:
            logger.error("No card update information found in event")
            return False
        
        # Extract updated card details
        new_expiry_date = updated_card_data.get("expiry")
        new_card_status = updated_card_data.get("status")
        
        # Format expiry date if needed (PayPal format: YYYY-MM to MM/YYYY)
        if new_expiry_date:
            try:
                year, month = new_expiry_date.split("-")
                formatted_expiry = f"{month}/{year}"
            except ValueError:
                formatted_expiry = new_expiry_date
        else:
            formatted_expiry = None
        
        # Prepare attributes to update
        attributes = {}
        if formatted_expiry:
            attributes["expiry_date"] = formatted_expiry
        if new_card_status:
            attributes["status"] = new_card_status
        
        if not attributes:
            logger.info("No attributes to update")
            return True
        
        # Update card in database
        from anthropic_api import update_card_by_subscription_id
        result = update_card_by_subscription_id(subscription_id, attributes)
        
        logger.info(f"Card update result: {result}")
        return True
    except Exception as e:
        logger.error(f"Database update error: {str(e)}")
        return False

@router.post("/paypal/card-updated")
async def webhook_card_updated(request: Request):
    """
    Handle PayPal Account Updater webhook events for card updates.
    
    Args:
        request: The incoming webhook request
        
    Returns:
        JSONResponse: Confirmation of webhook processing
    """
    try:
        # Verify webhook signature
        is_valid = await verify_webhook_signature(request)
        if not is_valid:
            logger.warning("Invalid webhook signature")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse webhook payload
        body = await request.body()
        event_data = json.loads(body)
        
        # Log webhook event
        event_type = event_data.get("event_type", "unknown")
        logger.info(f"Received PayPal webhook: {event_type}")
        
        # Process different event types
        if event_type == "ACCOUNT.STATUS.UPDATED":
            # Handle card update event
            success = await update_card_in_database(event_data)
            if not success:
                logger.error("Failed to update card in database")
                return JSONResponse(
                    status_code=500,
                    content={"status": "error", "message": "Failed to process card update"}
                )
            
            return JSONResponse(
                content={"status": "success", "message": "Card updated successfully"}
            )
        else:
            # Log unhandled event type
            logger.info(f"Unhandled event type: {event_type}")
            return JSONResponse(
                content={"status": "success", "message": "Event acknowledged but not processed"}
            )
    
    except json.JSONDecodeError:
        logger.error("Invalid JSON payload")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing webhook: {str(e)}")