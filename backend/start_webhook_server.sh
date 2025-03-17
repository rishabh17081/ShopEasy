#!/bin/bash

# Start the PayPal webhook server
echo "Starting PayPal webhook server..."
cd "$(dirname "$0")"
python3 -m app.events.webhook_card_update
