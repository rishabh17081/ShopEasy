import logging
import requests
import json
from typing import Dict, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("anthropic_api")

# Database API endpoint (adjust this to match your actual database API)
DB_API_ENDPOINT = "http://localhost:8000/api"

def update_card_by_subscription_id(subscription_id: str, attributes: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update card attributes in the database using the subscription_id as identifier.
    
    Args:
        subscription_id: The PayPal subscription ID for the card
        attributes: Dictionary of attributes to update
        
    Returns:
        Dict: Response from the database API
    """
    try:
        logger.info(f"Updating card with subscription_id {subscription_id}")
        logger.info(f"Attributes to update: {attributes}")
        
        # Make API call to your database service
        response = requests.put(
            f"{DB_API_ENDPOINT}/cards/subscription/{subscription_id}",
            json=attributes
        )
        
        # Check if request was successful
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Card updated successfully: {result}")
            return {"success": True, "data": result}
        else:
            logger.error(f"Failed to update card: {response.status_code} - {response.text}")
            return {"success": False, "error": f"API error: {response.status_code}"}
    
    except requests.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        return {"success": False, "error": f"Request error: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {"success": False, "error": f"Unexpected error: {str(e)}"}

def get_card_by_subscription_id(subscription_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve card information from the database using subscription_id.
    
    Args:
        subscription_id: The PayPal subscription ID for the card
        
    Returns:
        Optional[Dict]: Card information if found, None otherwise
    """
    try:
        logger.info(f"Getting card with subscription_id {subscription_id}")
        
        # Make API call to your database service
        response = requests.get(
            f"{DB_API_ENDPOINT}/cards/subscription/{subscription_id}"
        )
        
        # Check if request was successful
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Card retrieved successfully")
            return result
        elif response.status_code == 404:
            logger.warning(f"Card with subscription_id {subscription_id} not found")
            return None
        else:
            logger.error(f"Failed to retrieve card: {response.status_code} - {response.text}")
            return None
    
    except requests.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return None

def create_subscription_record(card_id: int, subscription_id: str) -> Dict[str, Any]:
    """
    Create a record of a new PayPal account updater subscription.
    
    Args:
        card_id: The internal database ID for the card
        subscription_id: The PayPal subscription ID
        
    Returns:
        Dict: Response from the database API
    """
    try:
        logger.info(f"Creating subscription record for card_id {card_id}")
        
        # Make API call to your database service
        response = requests.post(
            f"{DB_API_ENDPOINT}/cards/{card_id}/subscription",
            json={"subscription_id": subscription_id}
        )
        
        # Check if request was successful
        if response.status_code == 201:
            result = response.json()
            logger.info(f"Subscription record created successfully: {result}")
            return {"success": True, "data": result}
        else:
            logger.error(f"Failed to create subscription record: {response.status_code} - {response.text}")
            return {"success": False, "error": f"API error: {response.status_code}"}
    
    except requests.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        return {"success": False, "error": f"Request error: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {"success": False, "error": f"Unexpected error: {str(e)}"}