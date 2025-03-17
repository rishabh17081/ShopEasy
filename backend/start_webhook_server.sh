#!/bin/bash

# Start the PayPal webhook server
echo "Starting PayPal webhook server..."
# Change to the backend directory
cd "$(dirname "$0")"
# Run the webhook server module
python3 -m app.events.webhook_card_update
