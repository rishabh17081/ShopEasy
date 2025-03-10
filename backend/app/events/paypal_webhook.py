import json
import logging
import hmac
import hashlib
import base64
from flask import request, current_app
from typing import Dict, Any, Optional, Tuple
from app.events.merchant_db_connector import update_card_by_subscription_id

# Set up logging
logger = logging.getLogger(__name__)

# PayPal webhook event types
EVENT_ACCOUNT_STATUS_UPDATED = "PAYMENT.ACCOUNT-STATUS.UPDATED"


def verify_webhook_signature(webhook_payload: bytes, signature_header: str, webhook_secret: str) -> bool:
    """
    Verify that the webhook signature is valid and the request is genuinely from PayPal.
    
    Args:
        webhook_payload: Raw webhook request body
        signature_header: PayPal-Signature header value
        webhook_secret: Your PayPal webhook secret
    
    Returns:
        bool: True if signature is valid, False otherwise
    """
    if not signature_header or not webhook_secret:
        logger.error("Missing signature header or webhook secret")
        return False
    
    try:
        # Parse signature header
        signature_parts = {}
        for part in signature_header.split(','):
            key_value = part.strip().split('=')
            if len(key_value) == 2:
                signature_parts[key_value[0]] = key_value[1]
        
        # Get expected signature components
        algorithm = signature_parts.get('algorithm', '')
        signature = signature_parts.get('signature', '')
        transmission_id = signature_parts.get('transmission_id', '')
        transmission_time = signature_parts.get('transmission_time', '')
        
        if not all([algorithm, signature, transmission_id, transmission_time]):
            logger.error("Missing required signature components")
            return False
        
        # Decode the signature
        decoded_signature = base64.b64decode(signature)
        
        # Create the expected signature
        data_to_sign = transmission_id + '|' + transmission_time + '|' + webhook_payload.decode('utf-8') + '|' + webhook_secret
        
        # Generate hash
        if algorithm.lower() == 'sha256':
            expected_signature = hmac.new(
                webhook_secret.encode('utf-8'),
                data_to_sign.encode('utf-8'),
                hashlib.sha256
            ).digest()
            
            # Compare signatures
            return hmac.compare_digest(expected_signature, decoded_signature)
        else:
            logger.error(f"Unsupported signature algorithm: {algorithm}")
            return False
            
    except Exception as e:
        logger.error(f"Error verifying webhook signature: {str(e)}")
        return False


def process_webhook_event(event_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Process a PayPal webhook event.
    
    Args:
        event_data: Parsed webhook event data
    
    Returns:
        Tuple[bool, Optional[str]]: Success status and message or error
    """
    try:
        # Get the event type
        event_type = event_data.get('event_type')
        if not event_type:
            return False, "Missing event_type in webhook payload"
        
        # Log the event
        logger.info(f"Processing PayPal webhook event: {event_type}")
        
        # Handle different event types
        if event_type == EVENT_ACCOUNT_STATUS_UPDATED:
            return handle_account_status_updated(event_data)
        else:
            logger.info(f"Ignoring unhandled event type: {event_type}")
            return True, f"Event type {event_type} not processed but acknowledged"
            
    except Exception as e:
        logger.error(f"Error processing webhook event: {str(e)}")
        return False, f"Error processing webhook: {str(e)}"


def handle_account_status_updated(event_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Handle the PAYMENT.ACCOUNT-STATUS.UPDATED event which is triggered when 
    card details like expiry date are updated.
    
    Args:
        event_data: Webhook event data
    
    Returns:
        Tuple[bool, Optional[str]]: Success status and message or error
    """
    try:
        # Get the resource data (account info)
        resource = event_data.get('resource', {})
        if not resource:
            return False, "Missing resource data in webhook payload"
        
        # Extract subscription ID and updated card details
        subscription_id = resource.get('id')
        if not subscription_id:
            return False, "Missing subscription ID in resource data"
        
        # Extract card details that might have changed
        updated_attributes = {}
        
        # Extract expiry date if present (format should be YYYY-MM)
        if 'expiry' in resource:
            expiry_data = resource.get('expiry', {})
            month = expiry_data.get('month')
            year = expiry_data.get('year')
            
            if month and year:
                # Convert to MM/YYYY format for our database
                expiry_date = f"{str(month).zfill(2)}/{year}"
                updated_attributes['expiry_date'] = expiry_date
        
        # Other potential updates could include card status, etc.
        
        if not updated_attributes:
            return True, "No attributes to update were found in the webhook"
        
        # Update the card in our database using the subscription ID
        update_result = update_card_by_subscription_id(subscription_id, updated_attributes)
        
        if update_result.get('success', False):
            logger.info(f"Successfully updated card with subscription ID {subscription_id}")
            return True, f"Card with subscription ID {subscription_id} updated successfully"
        else:
            error_message = update_result.get('error', 'Unknown error')
            logger.error(f"Failed to update card: {error_message}")
            return False, f"Failed to update card: {error_message}"
            
    except Exception as e:
        logger.error(f"Error handling account status update: {str(e)}")
        return False, f"Error handling account status update: {str(e)}"
