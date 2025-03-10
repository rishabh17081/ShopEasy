import os
import json
import logging
import httpx
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration - In production, use environment variables
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "YOUR_ANTHROPIC_API_KEY")
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_MODEL = "claude-3-opus-20240229"

class AnthropicReconciliation:
    """
    Class to handle card update reconciliation using Anthropic's AI
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize with API key
        """
        self.api_key = api_key or ANTHROPIC_API_KEY
        self.headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
    
    async def reconcile_card_updates(
        self, 
        paypal_data: Dict[str, Any], 
        database_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Reconcile differences between PayPal card update and database record
        
        Args:
            paypal_data: Card data from PayPal update event
            database_data: Current card data from the database
            
        Returns:
            Dict with reconciled card data and confidence score
        """
        try:
            # Prepare the prompt
            prompt = self._create_reconciliation_prompt(paypal_data, database_data)
            
            # Call Anthropic API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    ANTHROPIC_API_URL,
                    headers=self.headers,
                    json={
                        "model": ANTHROPIC_MODEL,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": 1000
                    },
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    logger.error(f"Anthropic API error: {response.status_code} - {response.text}")
                    return {"error": "API error", "status_code": response.status_code}
                
                result = response.json()
                
            # Parse the AI response
            ai_content = result.get("content", [])
            if not ai_content or not isinstance(ai_content, list):
                return {"error": "Invalid API response format"}
                
            ai_text = "".join([block.get("text", "") for block in ai_content if block.get("type") == "text"])
            
            # Extract reconciled data from AI response
            reconciled_data = self._parse_reconciliation_response(ai_text)
            
            return {
                "status": "success",
                "reconciled_data": reconciled_data,
                "confidence": reconciled_data.get("confidence", 0.0),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in reconciliation: {str(e)}")
            return {"error": str(e)}
    
    def _create_reconciliation_prompt(
        self, 
        paypal_data: Dict[str, Any], 
        database_data: Dict[str, Any]
    ) -> str:
        """
        Create a prompt for the AI to reconcile card data
        """
        return f"""
        You are an expert in payment card data reconciliation. I need you to compare and reconcile 
        the following two sets of card data - one from PayPal and one from our database.
        
        ## PayPal Card Update Data:
        ```json
        {json.dumps(paypal_data, indent=2)}
        ```
        
        ## Current Database Record:
        ```json
        {json.dumps(database_data, indent=2)}
        ```
        
        Please analyze these records and:
        1. Identify all differences between the two records
        2. Determine which values should be kept for each field
        3. Create a reconciled version of the card data
        4. Provide a confidence score (0.0 to 1.0) for your reconciliation
        5. Return your answer as a JSON object with the following structure:
        
        ```json
        {{
          "reconciled_data": {{
            "card_brand": "VISA/MASTERCARD/etc",
            "last_four": "1234",
            "expiry_month": "MM",
            "expiry_year": "YYYY",
            "card_status": "ACTIVE/EXPIRED/etc",
            "is_default": true/false
          }},
          "differences": [
            {{
              "field": "field_name",
              "paypal_value": "value from paypal",
              "database_value": "value from database",
              "resolution": "explanation of your decision"
            }}
          ],
          "confidence": 0.95
        }}
        ```
        
        Only return the JSON with no additional text.
        """
    
    def _parse_reconciliation_response(self, ai_text: str) -> Dict[str, Any]:
        """
        Parse the AI response to extract reconciled data
        
        Args:
            ai_text: Text response from Anthropic API
            
        Returns:
            Dict containing reconciled data
        """
        try:
            # Try to extract JSON from the response
            json_start = ai_text.find('{')
            json_end = ai_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = ai_text[json_start:json_end]
                result = json.loads(json_str)
                
                # Basic validation
                if not isinstance(result, dict):
                    logger.warning("AI response is not a dictionary")
                    return {"error": "Invalid response format"}
                
                if "reconciled_data" not in result:
                    logger.warning("AI response missing reconciled_data")
                    return {"error": "Missing reconciled data"}
                
                return result
            else:
                logger.warning("Could not find JSON in AI response")
                logger.debug(f"AI response: {ai_text}")
                return {"error": "No JSON found in response"}
                
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing AI response: {str(e)}")
            logger.debug(f"AI response: {ai_text}")
            return {"error": f"JSON parse error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error parsing AI response: {str(e)}")
            return {"error": str(e)}

async def reconcile_card_update(
    subscription_id: str,
    paypal_data: Dict[str, Any], 
    database_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Convenience function to reconcile card updates
    
    Args:
        subscription_id: PayPal subscription ID
        paypal_data: Card data from PayPal update
        database_data: Current card data in database
        
    Returns:
        Dict with reconciliation results
    """
    reconciler = AnthropicReconciliation()
    result = await reconciler.reconcile_card_updates(paypal_data, database_data)
    
    if "error" in result:
        logger.error(f"Reconciliation error for subscription {subscription_id}: {result['error']}")
        return {"status": "error", "message": result["error"]}
    
    logger.info(f"Reconciliation complete for subscription {subscription_id} with confidence {result.get('confidence', 0)}")
    return result
