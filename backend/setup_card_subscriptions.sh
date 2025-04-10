#!/bin/bash

# Run the migration to add the subscription_id column
echo "Running migration to add subscription_id column..."
./run_migration.sh

# Wait for the migration to complete
sleep 2

# Run the card subscription manager to subscribe all cards
echo "Subscribing cards to PayPal Account Updater..."
python -c "from app.events.card_subscription_manager import subscribe_all_cards; subscribe_all_cards()"

echo "Card subscription setup complete!"
