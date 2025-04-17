from flask import Blueprint, request, jsonify
import os
import sys
import json
import logging

# Configure logging
try:
    log_dir = os.path.dirname(os.path.abspath(__file__))
    log_path = os.path.join(log_dir, 'chatbot_api.log')
    
    # Ensure log directory exists
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    logger.info('API logging initialized successfully at %s', log_path)
except Exception as e:
    # Fallback to just console logging if file logging fails
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    logger = logging.getLogger(__name__)
    logger.warning('Failed to initialize file logging: %s. Falling back to console logging.', str(e))

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

# Import the AnthropicToolsHandler (using absolute import path to avoid conflicts)
import sys
import os.path
# Remove any existing paths to avoid conflicts
if '/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages' in sys.path:
    sys.path.remove('/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages')
# Add our project's path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)
from chatbot.shopeasy_ecommerce_agent import AnthropicToolsHandler, PayPalAPI

chatbot_bp = Blueprint('chatbot', __name__)

# Initialize the AnthropicToolsHandler
handler = None

def get_handler():
    """
    Get or initialize the AnthropicToolsHandler.
    """
    global handler
    if handler is None:
        # Validate required environment variables
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        
        paypal_token = os.environ.get("PAYPAL_ACCESS_TOKEN")
        if not paypal_token:
            raise ValueError("PAYPAL_ACCESS_TOKEN environment variable is not set")
        
        # Get PayPal sandbox setting
        is_sandbox = os.environ.get("PAYPAL_SANDBOX", "true").lower() == "true"
        logger.info("Initializing PayPal API in %s mode", "sandbox" if is_sandbox else "production")
        
        handler = AnthropicToolsHandler(
            api_key=api_key,
            model_name="claude-3-opus-20240229",
            temperature=0.7,
            max_tokens=4096,
            system_message="You are a helpful AI assistant for an e-commerce website.",
            paypal_api=PayPalAPI(),
            paypal_context={"sandbox": is_sandbox, "merchant_id": "demo_merchant_id"}
        )
        logger.info("Successfully initialized AnthropicToolsHandler")
    
    return handler

@chatbot_bp.route('/query', methods=['POST'])
def query():
    """
    Query the Anthropic model with tools.
    """
    try:
        data = request.json
        if not data or 'query' not in data:
            logger.warning('Missing query parameter in request')
            return jsonify({"error": "Missing query parameter"}), 400
        
        query_text = data['query']
        chat_history = data.get('chat_history', [])
        execute_tools = data.get('execute_tools', True)
        
        logger.info('Processing query: %s', query_text)
        logger.debug('Chat history length: %d, Execute tools: %s', len(chat_history), execute_tools)
        
        # Get the handler
        try:
            handler = get_handler()
        except Exception as e:
            logger.error('Failed to initialize handler: %s', str(e), exc_info=True)
            return jsonify({"error": "Failed to initialize chatbot handler"}), 500
        
        # Get PayPal tools
        try:
            paypal_tools = handler.create_paypal_tools()
        except Exception as e:
            logger.error('Failed to create PayPal tools: %s', str(e), exc_info=True)
            return jsonify({"error": "Failed to initialize PayPal tools"}), 500
        
        # Query with PayPal tools
        try:
            result = handler.query_with_tools(
                query=query_text,
                tools=paypal_tools,
                chat_history=chat_history,
                execute_tools=execute_tools
            )
            logger.info('Successfully processed query')
            return jsonify(result)
        except Exception as e:
            logger.error('Error processing query: %s', str(e), exc_info=True)
            return jsonify({"error": "Error processing query" + str(e)}), 500
    
    except Exception as e:
        logger.error('Unexpected error in query endpoint: %s', str(e), exc_info=True)
        return jsonify({"error": "An unexpected error occurred"}), 500

@chatbot_bp.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint.
    """
    return jsonify({"status": "ok"})
