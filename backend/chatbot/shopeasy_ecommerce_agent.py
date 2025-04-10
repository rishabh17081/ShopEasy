"""
Module for integrating Anthropic Claude with LangChain tools.
This module provides functionality to use Anthropic's Claude model with tools via LangChain,
specifically integrating with PayPal API functions.
"""

import os
import json
import asyncio
import base64
import io
# Set matplotlib backend to non-interactive Agg to avoid GUI issues in async environments
import matplotlib
matplotlib.use('Agg')  # Must be set before importing pyplot
import matplotlib.pyplot as plt
from typing import List, Dict, Any, Optional, Union, Callable
from collections import Counter

from langchain.tools import BaseTool, Tool
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Import PayPal functions
import sys
import os.path
sys.path.append('/Users/rishabhsharma/PycharmProjects/ecommerce-site/backend/paypal-agent-toolkit/typescript/src/shared')
from functions import (
    create_invoice, list_invoices, send_invoice, send_invoice_reminder, cancel_sent_invoice,
    create_product, list_products, update_product,
    create_subscription_plan, list_subscription_plans,
    create_order, get_order,
    create_shipment, get_shipment_tracking
)

# Function to generate invoice insights with pie chart
async def generate_invoice_insights(
    paypal_api,
    context: Dict[str, Any],
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate business insights from invoices with a pie chart visualization based on status.
    
    Args:
        paypal_api: PayPal API client
        context: Context containing sandbox and merchant_id information
        params: Dictionary containing optional parameters like page, page_size, and total_required
        
    Returns:
        Dictionary containing insights and a base64-encoded pie chart image
    """
    print('[generateInvoiceInsights] Starting to generate invoice insights')
    print(f'[generateInvoiceInsights] Context: {json.dumps({"sandbox": context.get("sandbox"), "merchant_id": context.get("merchant_id")})}')
    
    # Get invoices using the existing list_invoices function
    try:
        # Set a larger page_size to get more data for analysis
        params_with_defaults = {
            'page': params.get('page', 1),
            'page_size': params.get('page_size', 100),  # Get up to 100 invoices for analysis
            'total_required': params.get('total_required', True)
        }
        
        print(f'[generateInvoiceInsights] Fetching invoices with params: {json.dumps(params_with_defaults)}')
        invoices_data = await list_invoices(paypal_api, context, params_with_defaults)
        
        if 'items' not in invoices_data or not isinstance(invoices_data['items'], list):
            print('[generateInvoiceInsights] No invoices found or invalid response format')
            return {
                'error': 'No invoices found or invalid response format',
                'raw_response': invoices_data
            }
        
        invoices = invoices_data['items']
        total_invoices = len(invoices)
        print(f'[generateInvoiceInsights] Retrieved {total_invoices} invoices for analysis')
        
        if total_invoices == 0:
            return {
                'message': 'No invoices found for analysis',
                'chart': None,
                'insights': {
                    'total_invoices': 0,
                    'status_distribution': {}
                }
            }
        
        # Analyze invoices by status
        status_counts = Counter()
        amount_by_status = {}
        total_amount = 0
        currencies = set()
        
        for invoice in invoices:
            status = invoice.get('status', 'UNKNOWN')
            status_counts[status] += 1
            
            # Extract amount information if available
            if 'amount' in invoice and 'value' in invoice['amount']:
                amount = float(invoice['amount']['value'])
                currency = invoice['amount'].get('currency_code', 'USD')
                currencies.add(currency)
                
                if status not in amount_by_status:
                    amount_by_status[status] = 0
                amount_by_status[status] += amount
                total_amount += amount
        
        # Generate pie chart for status distribution
        plt.figure(figsize=(10, 6))
        
        # Create a pie chart
        labels = list(status_counts.keys())
        sizes = list(status_counts.values())
        
        # Use a colorful palette
        colors = plt.cm.Paired(range(len(labels)))
        
        # Create the pie chart with percentage labels
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors)
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        plt.title('Invoice Distribution by Status')
        
        # Save the chart to a bytes buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        
        # Convert the image to base64 for embedding in HTML or JSON
        chart_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        # Calculate percentages for the insights
        status_percentages = {status: (count / total_invoices) * 100 for status, count in status_counts.items()}
        
        # Generate insights text
        insights = {
            'total_invoices': total_invoices,
            'status_distribution': {
                status: {
                    'count': count,
                    'percentage': status_percentages[status]
                } for status, count in status_counts.items()
            },
            'summary': f"Analysis of {total_invoices} invoices shows: " + 
                      ", ".join([f"{count} {status} ({status_percentages[status]:.1f}%)" 
                                for status, count in status_counts.most_common()])
        }
        
        # Add financial insights if available
        if amount_by_status:
            insights['financial'] = {
                'total_amount': total_amount,
                'currency': list(currencies)[0] if len(currencies) == 1 else list(currencies),
                'amount_by_status': amount_by_status
            }
        
        print(f'[generateInvoiceInsights] Generated insights for {total_invoices} invoices')
        
        return {
            'chart': chart_base64,
            'insights': insights,
            'chart_type': 'pie',
            'chart_title': 'Invoice Distribution by Status'
        }
        
    except Exception as error:
        print(f'[generateInvoiceInsights] Error generating invoice insights: {str(error)}')
        return {
            'error': f'Error generating invoice insights: {str(error)}'
        }

# Mock PayPal API client for demonstration purposes
class PayPalAPI:
    async def get_headers(self):
        return {"Authorization": "Bearer A21AAKv4Ez5u2QNgDmBABYdFgVj4mNOSigmDRaykBTpRbiBrXWSMHIJ2k9lXb278qMMIsfQeOO3jVm5yH89pxQTbZ4JHJpLuA", "Content-Type": "application/json"}
    
    def get_base_url(self):
        return "https://api.sandbox.paypal.com"


class AnthropicToolsHandler:
    """
    Handler for using Anthropic Claude with LangChain tools, specifically for PayPal API integration.
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        model_name: str = "claude-3-7-sonnet-20250219",
        temperature: float = 0.7,
        max_tokens: int = 10000,
        system_message: Optional[str] = None,
        paypal_api: Optional[Any] = None,
        paypal_context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the Anthropic Tools Handler.
        
        Args:
            api_key: Anthropic API key. If not provided, will look for ANTHROPIC_API_KEY env var.
            model_name: Anthropic model to use (default: claude-3-opus-20240229)
            temperature: Temperature for generation (0.0 to 1.0)
            max_tokens: Maximum tokens to generate in the response
            system_message: Optional system message to provide context to the model
            paypal_api: PayPal API client instance
            paypal_context: PayPal context information (sandbox, merchant_id, etc.)
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key must be provided or set as ANTHROPIC_API_KEY environment variable")
        
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.system_message = system_message or "You are a helpful AI assistant."
        
        # Initialize the Anthropic client
        self.client = ChatAnthropic(
            anthropic_api_key=self.api_key,
            model_name=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        # Initialize PayPal API client and context
        self.paypal_api = paypal_api or PayPalAPI()
        self.paypal_context = paypal_context or {"sandbox": True, "merchant_id": "mock_merchant_id"}
    
    def create_paypal_tools(self) -> List[BaseTool]:
        """
        Create LangChain tools for PayPal API functions.
        
        Returns:
            List of LangChain tools for PayPal API functions
        """
        # Create a wrapper for async functions to be used with LangChain tools
        def async_wrapper(func: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                return asyncio.run(func(*args, **kwargs))
            return wrapper
        
        # Invoice tools
        create_invoice_tool = Tool(
            name="create_invoice",
            func=async_wrapper(lambda data: create_invoice(self.paypal_api, self.paypal_context, data)),
            description="Create a draft invoice in PayPal and then send it to the customer. Required parameters: detail, invoicer, primary_recipients, amount."
        )
        
        list_invoices_tool = Tool(
            name="list_invoices",
            func=async_wrapper(lambda params: list_invoices(self.paypal_api, self.paypal_context, params)),
            description="List invoices from PayPal. Optional parameters: page, page_size, total_required."
        )
        
        send_invoice_tool = Tool(
            name="send_invoice",
            func=async_wrapper(lambda params: send_invoice(self.paypal_api, self.paypal_context, params)),
            description="Send an invoice to a recipient. Required parameter: invoice_id. Optional parameters: note, send_to_recipient, additional_recipients."
        )
        
        send_invoice_reminder_tool = Tool(
            name="send_invoice_reminder",
            func=async_wrapper(lambda params: send_invoice_reminder(self.paypal_api, self.paypal_context, params)),
            description="Send a reminder for an invoice. Required parameter: invoice_id. Optional parameters: subject, note, additional_recipients."
        )
        
        cancel_sent_invoice_tool = Tool(
            name="cancel_sent_invoice",
            func=async_wrapper(lambda params: cancel_sent_invoice(self.paypal_api, self.paypal_context, params)),
            description="Cancel a sent invoice. Required parameter: invoice_id. Optional parameters: note, send_to_recipient, additional_recipients."
        )
        
        # Product tools
        create_product_tool = Tool(
            name="create_product",
            func=async_wrapper(lambda params: create_product(self.paypal_api, self.paypal_context, params)),
            description="Create a product in PayPal. Required parameters: name, type. Optional parameters: description, category, image_url, home_url."
        )
        
        list_products_tool = Tool(
            name="list_products",
            func=async_wrapper(lambda params: list_products(self.paypal_api, self.paypal_context, params)),
            description="List products from PayPal. Optional parameters: page, page_size, total_required."
        )
        
        update_product_tool = Tool(
            name="update_product",
            func=async_wrapper(lambda params: update_product(self.paypal_api, self.paypal_context, params)),
            description="Update a product in PayPal. Required parameters: product_id, operations (array of patch operations)."
        )
        
        # Subscription plan tools
        create_subscription_plan_tool = Tool(
            name="create_subscription_plan",
            func=async_wrapper(lambda params: create_subscription_plan(self.paypal_api, self.paypal_context, params)),
            description="Create a subscription plan in PayPal. Required parameters: product_id, name, billing_cycles. Optional parameters: description, payment_preferences, taxes."
        )
        
        list_subscription_plans_tool = Tool(
            name="list_subscription_plans",
            func=async_wrapper(lambda params: list_subscription_plans(self.paypal_api, self.paypal_context, params)),
            description="List subscription plans from PayPal. Optional parameters: product_id, page, page_size, total_required."
        )
        
        # Order tools
        create_order_tool = Tool(
            name="create_order",
            func=async_wrapper(lambda params: create_order(None, params)),  # PayPal client would be passed here in a real implementation
            description="Create an order in PayPal. Required parameters depend on the order type."
        )
        
        get_order_tool = Tool(
            name="get_order",
            func=async_wrapper(lambda params: get_order(None, params)),  # PayPal client would be passed here in a real implementation
            description="Get an order from PayPal. Required parameter: id (order ID)."
        )
        
        # Tracking tools
        create_shipment_tool = Tool(
            name="create_shipment",
            func=async_wrapper(lambda params: create_shipment(self.paypal_api, self.paypal_context, params)),
            description="Create a shipment tracking in PayPal. Required parameters: tracking_number, transaction_id, status, carrier."
        )
        
        get_shipment_tracking_tool = Tool(
            name="get_shipment_tracking",
            func=async_wrapper(lambda params: get_shipment_tracking(self.paypal_api, self.paypal_context, params)),
            description="Get shipment tracking information from PayPal. Required parameters: transaction_id, tracking_number."
        )
        
        # Invoice insights tool
        generate_invoice_insights_tool = Tool(
            name="generate_invoice_insights",
            func=async_wrapper(lambda params: generate_invoice_insights(self.paypal_api, self.paypal_context, params)),
            description="Generate business insights from invoices with a pie chart visualization based on status. Optional parameters: page, page_size, total_required."
        )
        
        return [
            create_invoice_tool,
            list_invoices_tool,
            generate_invoice_insights_tool,
            send_invoice_tool,
            send_invoice_reminder_tool,
            cancel_sent_invoice_tool,
            create_product_tool,
            list_products_tool,
            update_product_tool,
            create_subscription_plan_tool,
            list_subscription_plans_tool,
            create_order_tool,
            get_order_tool,
            create_shipment_tool,
            get_shipment_tracking_tool,
        ]
    
    def create_chain_with_tools(self, tools: List[BaseTool]) -> Any:
        """
        Create a LangChain chain that can use tools with Anthropic Claude.
        
        Args:
            tools: List of LangChain tools to make available to the model
            
        Returns:
            A LangChain runnable chain that can process messages and tools
        """
        # Create a prompt template with tool instructions
        tool_descriptions = "\n".join([
            f"- {tool.name}: {tool.description}" for tool in tools
        ])
        
        tool_system_message = f"""You have access to the following tools:

{tool_descriptions}

To use a tool, respond with:
```
<tool>
<tool_name>NAME_OF_TOOL</tool_name>
<tool_input>
{{{{
    "param1": "value1",
    "param2": "value2"
}}}}
</tool_input>
</tool>
```

Only use the tools when necessary. If you don't need to use a tool, just respond normally.
"""
        
        # Combine with the base system message
        combined_system_message = f"{self.system_message}\n\n{tool_system_message}"
        
        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", combined_system_message),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        # Create the chain
        chain = (
            {"messages": RunnablePassthrough()}
            | prompt
            | self.client
            | StrOutputParser()
        )
        
        return chain
    
    def query_with_tools(
        self, 
        query: str, 
        tools: List[BaseTool], 
        chat_history: Optional[List[Union[HumanMessage, AIMessage, ToolMessage]]] = None,
        execute_tools: bool = False
    ) -> Dict[str, Any]:
        """
        Query the Anthropic model with tools available.
        
        Args:
            query: User query text
            tools: List of LangChain tools to make available
            chat_history: Optional chat history for context
            execute_tools: Whether to execute the tool calls
            
        Returns:
            Dictionary containing the model's response, tool calls, and tool results if executed
        """
        # Initialize chat history if not provided
        if chat_history is None:
            chat_history = []
        
        # Create the chain with tools
        chain = self.create_chain_with_tools(tools)
        
        # Add the new query to messages
        messages = chat_history + [HumanMessage(content=query)]
        
        # Get the response
        response = chain.invoke(messages)
        
        # Parse the response to extract tool calls
        tool_calls = []
        if "<tool>" in response:
            # Extract all tool calls
            start_idx = 0
            while True:
                tool_start = response.find("<tool>", start_idx)
                if tool_start == -1:
                    break
                    
                tool_end = response.find("</tool>", tool_start)
                if tool_end == -1:
                    break
                    
                tool_text = response[tool_start:tool_end + 7]
                
                # Extract tool name
                name_start = tool_text.find("<tool_name>") + len("<tool_name>")
                name_end = tool_text.find("</tool_name>", name_start)
                if name_end > name_start:
                    tool_name = tool_text[name_start:name_end].strip()
                    
                    # Extract tool input
                    input_start = tool_text.find("<tool_input>") + len("<tool_input>")
                    input_end = tool_text.find("</tool_input>", input_start)
                    if input_end > input_start:
                        tool_input_str = tool_text[input_start:input_end].strip()
                        
                        # Parse the JSON input
                        try:
                            # Fix common JSON formatting issues
                            fixed_input_str = tool_input_str.replace('\n', ' ').strip()
                            # Add missing commas between key-value pairs
                            fixed_input_str = fixed_input_str.replace('} {', '}, {')
                            fixed_input_str = fixed_input_str.replace('" "', '", "')
                            fixed_input_str = fixed_input_str.replace('} "', '}, "')
                            fixed_input_str = fixed_input_str.replace('" {', '", {')
                            
                            # Add commas between key-value pairs that are missing them
                            import re
                            fixed_input_str = re.sub(r'(\d+|\btrue\b|\bfalse\b|\bnull\b|"[^"]*")\s+(".*?":|[a-zA-Z_][a-zA-Z0-9_]*:)', r'\1, \2', fixed_input_str)
                            
                            # Try to parse the fixed JSON
                            tool_input = json.loads(fixed_input_str)
                            tool_calls.append({
                                "name": tool_name,
                                "input": tool_input
                            })
                        except json.JSONDecodeError as e:
                            print(f"Error parsing tool input JSON: {tool_input_str}")
                            print(f"JSON error: {str(e)}")
                            # Create a dictionary from key-value pairs manually as a fallback
                            try:
                                # Simple key-value extraction for basic cases
                                pairs = re.findall(r'"?([a-zA-Z_][a-zA-Z0-9_]*)"?\s*:\s*(".*?"|true|false|null|\d+(?:\.\d+)?)', tool_input_str)
                                tool_input = {}
                                for key, value in pairs:
                                    if value.startswith('"') and value.endswith('"'):
                                        tool_input[key] = value[1:-1]  # Remove quotes
                                    elif value.lower() == 'true':
                                        tool_input[key] = True
                                    elif value.lower() == 'false':
                                        tool_input[key] = False
                                    elif value.lower() == 'null':
                                        tool_input[key] = None
                                    else:
                                        try:
                                            if '.' in value:
                                                tool_input[key] = float(value)
                                            else:
                                                tool_input[key] = int(value)
                                        except ValueError:
                                            tool_input[key] = value
                                
                                if tool_input:  # Only add if we extracted something
                                    tool_calls.append({
                                        "name": tool_name,
                                        "input": tool_input
                                    })
                                    print(f"Manually extracted tool input: {json.dumps(tool_input)}")
                                else:
                                    print(f"Could not extract any key-value pairs from: {tool_input_str}")
                            except Exception as ex:
                                print(f"Error extracting key-value pairs: {str(ex)}")
                
                start_idx = tool_end + 7
        
        result = {
            "response": response,
            "tool_calls": tool_calls
        }
        
        # Execute tool calls if requested
        if execute_tools and tool_calls:
            tool_results = self.execute_tool_calls(tool_calls, tools)
            result["tool_results"] = tool_results
            
            # Add tool results to chat history as AIMessages instead of ToolMessages
            # since the current Anthropic library doesn't support ToolMessages
            for tool_call, tool_result in zip(tool_calls, tool_results):
                tool_result_content = f"Tool '{tool_call['name']}' result: {str(tool_result)}"
                tool_message = AIMessage(content=tool_result_content)
                chat_history.append(tool_message)
            
            # Get a follow-up response with the tool results
            follow_up_messages = chat_history + [
                AIMessage(content=response)
            ]
            
            try:
                follow_up_response = chain.invoke(follow_up_messages)
            except Exception as e:
                print(f"Error getting follow-up response: {str(e)}")
                follow_up_response = f"Error processing tool results: {str(e)}"
            result["follow_up_response"] = follow_up_response
        
        return result
    
    def execute_tool_calls(self, tool_calls: List[Dict[str, Any]], tools: List[BaseTool]) -> List[Any]:
        """
        Execute tool calls using the provided tools.
        
        Args:
            tool_calls: List of tool calls to execute
            tools: List of available tools
            
        Returns:
            List of tool execution results
        """
        tool_results = []
        
        # Create a mapping of tool names to tool objects
        tool_map = {tool.name: tool for tool in tools}
        
        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            tool_input = tool_call["input"]
            
            if tool_name in tool_map:
                tool = tool_map[tool_name]
                try:
                    # Execute the tool with the provided input
                    # For PayPal tools, we need to pass the entire dictionary as a single argument
                    # rather than unpacking it as keyword arguments
                    if tool_name.startswith("list_") or tool_name in ["create_invoice", "send_invoice", "send_invoice_reminder", "cancel_sent_invoice", "create_product", "update_product", "create_subscription_plan", "create_order", "get_order", "create_shipment", "get_shipment_tracking", "generate_invoice_insights"]:
                        result = tool.func(tool_input)
                    else:
                        # For other tools, use the standard approach
                        if isinstance(tool_input, dict):
                            result = tool.func(**tool_input)
                        else:
                            result = tool.func(tool_input)
                    
                    tool_results.append(result)
                except Exception as e:
                    error_message = f"Error executing tool {tool_name}: {str(e)}"
                    print(error_message)
                    tool_results.append({"error": error_message})
            else:
                error_message = f"Tool {tool_name} not found"
                print(error_message)
                tool_results.append({"error": error_message})
        
        return tool_results

# Example usage:
"""
# Initialize the handler with PayPal API client and context
handler = AnthropicToolsHandler(
    api_key="your_api_key",
    paypal_api=PayPalAPI(),
    paypal_context={"sandbox": True, "merchant_id": "your_merchant_id"}
)

# Get PayPal tools
paypal_tools = handler.create_paypal_tools()

# Query with PayPal tools
result = handler.query_with_tools(
    query="Create an invoice for $100 for web development services",
    tools=paypal_tools,
    execute_tools=True  # Set to True to execute the tool calls
)

print("Response:", result["response"])
print("Tool calls:", result["tool_calls"])
if "tool_results" in result:
    print("Tool results:", result["tool_results"])
if "follow_up_response" in result:
    print("Follow-up response:", result["follow_up_response"])
"""

def main():
    """
    Main function to demonstrate the usage of the AnthropicToolsHandler with PayPal tools.
    """
    # Initialize the handler
    handler = AnthropicToolsHandler(
        api_key='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',
        paypal_api=PayPalAPI(),
        paypal_context={"sandbox": True, "merchant_id": "demo_merchant_id"}
    )
    
    # Get PayPal tools
    paypal_tools = handler.create_paypal_tools()
    
    # Example query
    query = "List all invoices in my PayPal account"
    
    # Query with PayPal tools
    result = handler.query_with_tools(
        query=query,
        tools=paypal_tools,
        execute_tools=True
    )
    
    print("\n=== Query ===")
    print(query)
    
    print("\n=== Response ===")
    print(result["response"])
    
    print("\n=== Tool Calls ===")
    for i, tool_call in enumerate(result["tool_calls"]):
        print(f"Tool Call {i+1}:")
        print(f"  Name: {tool_call['name']}")
        print(f"  Input: {json.dumps(tool_call['input'], indent=2)}")
    
    if "tool_results" in result:
        print("\n=== Tool Results ===")
        for i, tool_result in enumerate(result["tool_results"]):
            print(f"Tool Result {i+1}:")
            print(f"  {json.dumps(tool_result, indent=2)}")
    
    if "follow_up_response" in result:
        print("\n=== Follow-up Response ===")
        print(result["follow_up_response"])

if __name__ == "__main__":
    main()
