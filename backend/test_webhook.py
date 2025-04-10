import requests
import json
import logging
import sys
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('test_webhook')

# Create a log file
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'webhook_test.log')
with open(log_file, 'w') as f:
    f.write("Starting webhook test script...\n")

# Print to console as well
print("Starting webhook test script...")

# Webhook server URL
WEBHOOK_URL = "http://localhost:8000/webhooks/card-updated"
print(f"Webhook URL: {WEBHOOK_URL}")

# Sample payload for testing with only required fields
sample_payload = {
    "expiry_date": "2032-01",  # New expiry date to update to
    "resource": {
        "update_type": "EXPIRY_UPDATE",
        "subscription_id": "SUB-TEST-39362488"  # This matches the subscription_id we just added
    }
}

def test_webhook():
    """
    Send a test webhook event to the webhook server
    """
    try:
        print(f"Sending test webhook event to {WEBHOOK_URL}")
        print(f"Payload: {json.dumps(sample_payload, indent=2)}")
        
        with open(log_file, 'a') as f:
            f.write(f"Sending test webhook event to {WEBHOOK_URL}\n")
            f.write(f"Payload: {json.dumps(sample_payload, indent=2)}\n")
        
        # Send the webhook event
        response = requests.post(
            WEBHOOK_URL,
            json=sample_payload,
            headers={"Content-Type": "application/json"}
        )
        
        # Check the response
        if response.status_code == 200:
            print(f"Webhook event sent successfully")
            print(f"Response: {response.json()}")
            with open(log_file, 'a') as f:
                f.write(f"Webhook event sent successfully\n")
                f.write(f"Response: {response.json()}\n")
        else:
            print(f"Failed to send webhook event: {response.status_code}")
            print(f"Response: {response.text}")
            with open(log_file, 'a') as f:
                f.write(f"Failed to send webhook event: {response.status_code}\n")
                f.write(f"Response: {response.text}\n")
        
        return response
    
    except Exception as e:
        print(f"Error sending webhook event: {str(e)}")
        import traceback
        print(traceback.format_exc())
        with open(log_file, 'a') as f:
            f.write(f"Error sending webhook event: {str(e)}\n")
            f.write(traceback.format_exc() + "\n")
        return None

if __name__ == "__main__":
    test_webhook()
