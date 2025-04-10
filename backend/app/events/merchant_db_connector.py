import sqlite3
import os
import sys
import logging
import traceback
from datetime import datetime

# Set up logging to both file and console
log_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
log_file = os.path.join(log_dir, 'card_subscriptions.log')

# Create a logger
logger = logging.getLogger('merchant_db_connector')
logger.setLevel(logging.DEBUG)  # Set to DEBUG level for more detailed logs

# Create handlers
file_handler = logging.FileHandler(log_file)
console_handler = logging.StreamHandler(sys.stdout)

# Create formatters and add to handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Prevent log propagation to avoid duplicate logs
logger.propagate = False

logger.info(f"Merchant DB connector logs will be written to {log_file}")

# Get the path to the database file
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'instance', 'ecommerce.db')
logger.info(f"Database path: {db_path}")

# Check if database file exists
if not os.path.exists(db_path):
    logger.error(f"Database file not found at {db_path}")
else:
    logger.info(f"Database file found at {db_path}")

def update_card_by_subscription_id(subscription_id, attributes):
    """
    Update a card in the database by subscription ID
    
    Args:
        subscription_id: The subscription ID of the card to update
        attributes: A dictionary of attributes to update
        
    Returns:
        dict: The updated card information or None if the card was not found
    """
    request_id = f"db-{os.urandom(4).hex()}"  # Generate a unique request ID for tracing
    logger.info(f"[{request_id}] Updating card with subscription ID {subscription_id}")
    logger.info(f"[{request_id}] Attributes to update: {attributes}")
    
    # Validate input parameters
    if not subscription_id:
        logger.error(f"[{request_id}] Missing subscription_id parameter")
        return None
        
    if not attributes or not isinstance(attributes, dict):
        logger.error(f"[{request_id}] Invalid attributes parameter: {attributes}")
        return None
    
    # Connect to the database
    conn = None
    cursor = None
    try:
        logger.debug(f"[{request_id}] Attempting to connect to database at {db_path}")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cursor = conn.cursor()
        logger.debug(f"[{request_id}] Successfully connected to database")
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"[{request_id}] Failed to connect to database: {str(e)}")
        logger.error(f"[{request_id}] Traceback: {tb}")
        return None
    
    try:
        # Check if the card exists
        query = "SELECT * FROM cards WHERE subscription_id = ?"
        logger.debug(f"[{request_id}] Executing query: {query} with params: ({subscription_id},)")
        
        cursor.execute(query, (subscription_id,))
        
        card = cursor.fetchone()
        if not card:
            logger.error(f"[{request_id}] Card with subscription ID {subscription_id} not found")
            return None
            
        logger.debug(f"[{request_id}] Found card: {dict(card)}")
        
        # Build the update query dynamically based on the provided attributes
        update_fields = []
        params = {"subscription_id": subscription_id}
        
        # Log all attributes and which ones are valid
        for key, value in attributes.items():
            if key in ['expiry_date', 'cardholder_name', 'card_number', 'last_four', 'card_type']:
                update_fields.append(f"{key} = :{key}")
                params[key] = value
                logger.debug(f"[{request_id}] Will update field '{key}' to '{value}'")
            else:
                logger.warning(f"[{request_id}] Ignoring invalid attribute '{key}'")
        
        if not update_fields:
            logger.warning(f"[{request_id}] No valid attributes to update")
            return dict(card)
        
        # Skip adding updated_at field since it doesn't exist in the database schema
        
        # Execute the update query
        query = f"UPDATE cards SET {', '.join(update_fields)} WHERE subscription_id = :subscription_id"
        logger.debug(f"[{request_id}] Executing update query: {query}")
        logger.debug(f"[{request_id}] Query parameters: {params}")
        
        cursor.execute(query, params)
        
        # Check if the update was successful
        if cursor.rowcount == 0:
            logger.error(f"[{request_id}] Failed to update card with subscription ID {subscription_id} - no rows affected")
            return None
            
        logger.debug(f"[{request_id}] Update successful, {cursor.rowcount} rows affected")
        
        # Commit the changes
        conn.commit()
        logger.debug(f"[{request_id}] Changes committed to database")
        
        # Get the updated card
        query = "SELECT * FROM cards WHERE subscription_id = ?"
        logger.debug(f"[{request_id}] Fetching updated card with query: {query}")
        
        cursor.execute(query, (subscription_id,))
        
        updated_card = cursor.fetchone()
        if updated_card:
            updated_card_dict = dict(updated_card)
            # Mask sensitive data in logs
            log_card = updated_card_dict.copy()
            if 'card_number' in log_card:
                log_card['card_number'] = '************' + log_card['card_number'][-4:] if log_card['card_number'] else None
            
            logger.info(f"[{request_id}] Successfully updated card with subscription ID {subscription_id}")
            logger.debug(f"[{request_id}] Updated card data: {log_card}")
            return updated_card_dict
        else:
            logger.error(f"[{request_id}] Could not fetch updated card after update")
            return None
    
    except sqlite3.Error as e:
        tb = traceback.format_exc()
        logger.error(f"[{request_id}] SQLite error updating card with subscription ID {subscription_id}: {str(e)}")
        logger.error(f"[{request_id}] Traceback: {tb}")
        if conn:
            conn.rollback()
            logger.debug(f"[{request_id}] Transaction rolled back")
        return None
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"[{request_id}] Unexpected error updating card with subscription ID {subscription_id}: {str(e)}")
        logger.error(f"[{request_id}] Traceback: {tb}")
        if conn:
            conn.rollback()
            logger.debug(f"[{request_id}] Transaction rolled back")
        return None
    
    finally:
        # Close the connection
        if cursor:
            cursor.close()
            logger.debug(f"[{request_id}] Database cursor closed")
        if conn:
            conn.close()
            logger.debug(f"[{request_id}] Database connection closed")
