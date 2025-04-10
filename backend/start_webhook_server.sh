#!/bin/bash

# Start the webhook server for PayPal Account Updater events
cd "$(dirname "$0")"
export PYTHONPATH=$PYTHONPATH:$(pwd)

echo "Starting webhook server on localhost:8000..."
python3 -c "from app.events.webhook_card_update import main; main()"

echo "Webhook server stopped."
