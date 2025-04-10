from flask import Blueprint, request, jsonify
import os
import sys
import json

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

# Import the AnthropicToolsHandler
from chatbot.anthropic_tools import AnthropicToolsHandler, PayPalAPI

chatbot_bp = Blueprint('chatbot', __name__)

# Initialize the AnthropicToolsHandler
handler = None

def get_handler():
    """
    Get or initialize the AnthropicToolsHandler.
    """
    global handler
    if handler is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        
        handler = AnthropicToolsHandler(
            api_key=api_key,
            model_name="claude-3-opus-20240229",
            temperature=0.7,
            max_tokens=4096,
            system_message="You are a helpful AI assistant for an e-commerce website.",
            paypal_api=PayPalAPI(),
            paypal_context={"sandbox": True, "merchant_id": "demo_merchant_id"}
        )
    
    return handler

@chatbot_bp.route('/query', methods=['POST'])
def query():
    """
    Query the Anthropic model with tools.
    """
    try:
        data = request.json
        if not data or 'query' not in data:
            return jsonify({"error": "Missing query parameter"}), 400
        
        query_text = data['query']
        chat_history = data.get('chat_history', [])
        execute_tools = data.get('execute_tools', True)
        
        # Get the handler
        handler = get_handler()
        
        # Get PayPal tools
        paypal_tools = handler.create_paypal_tools()
        
        # Query with PayPal tools
        result = handler.query_with_tools(
            query=query_text,
            tools=paypal_tools,
            chat_history=chat_history,
            execute_tools=execute_tools
        )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@chatbot_bp.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint.
    """
    return jsonify({"status": "ok"})
