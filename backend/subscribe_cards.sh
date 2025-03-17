#!/bin/bash

# Subscribe all cards to PayPal Account Updater
echo "Subscribing all cards to PayPal Account Updater..."
cd "$(dirname "$0")"
python3 -m app.events.subscribe_cards_to_paypal_au
