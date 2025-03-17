# Card Freshness Maintenance with PayPal Account Updater

This directory contains the implementation for maintaining card freshness using PayPal Account Updater (AU) service.

## Overview

PayPal Account Updater is a service that helps merchants keep their stored card information up-to-date. When card details change (e.g., expiry date updates, card replacements), PayPal AU notifies merchants through webhooks, allowing them to update their database automatically.

## Components

1. **subscribe_cards_to_paypal_au.py**: 
   - Contains functions to subscribe cards to PayPal AU service
   - Includes a utility to subscribe all existing cards in the database
   - Provides the `create_paypal_subscription()` function used by the card routes

2. **webhook_card_update.py**:
   - Implements a webhook server that listens for card update events from PayPal
   - Processes incoming events and updates the card information in the database
   - Runs on localhost:8000 and listens at the `/webhooks/card-updated` endpoint

3. **merchant_db_connector.py**:
   - Provides database utilities for updating card information
   - Includes the `update_card_by_subscription_id()` function used by the webhook handler

## Setup and Usage

### 1. Subscribe Cards to PayPal AU

To subscribe all existing cards in your database to PayPal AU:

```bash
./subscribe_cards.sh
```

This script will:
- Find all cards in the database that don't have a subscription_id
- Create a PayPal AU subscription for each card
- Update the cards in the database with their subscription IDs
- Log the results to `paypal_subscription.log`

### 2. Start the Webhook Server

To start the webhook server that listens for card update events:

```bash
./start_webhook_server.sh
```

This will:
- Start a Flask server on localhost:8000
- Listen for POST requests at `/webhooks/card-updated`
- Process incoming events and update card information in the database
- Log all activities to `paypal_webhook.log`

### 3. Configure PayPal to Send Webhooks

In your PayPal Developer Dashboard:
1. Go to Webhooks settings
2. Add a new webhook with the URL: `https://your-domain.com/webhooks/card-updated`
3. Select the `CARD.UPDATED` event type
4. Save the webhook configuration

For local development, you can use a service like ngrok to expose your local webhook server:

```bash
ngrok http 8000
```

Then use the ngrok URL in your PayPal webhook configuration.

## Automatic Card Updates

Once the system is set up:
1. New cards are automatically subscribed to PayPal AU when added (in `cards.py`)
2. When card details change, PayPal sends a webhook event
3. The webhook server processes the event and updates the card in the database
4. The updated card information is immediately available to your application

## Logs

- Subscription activities: `paypal_subscription.log`
- Webhook events: `paypal_webhook.log`

## Testing

You can test the webhook handler by sending a sample payload:

```bash
curl -X POST http://localhost:8000/webhooks/card-updated \
  -H "Content-Type: application/json" \
  -d '{
    "id": "WH-TEST123456789",
    "event_type": "CARD.UPDATED",
    "expiry_date": "2032-01",
    "resource": {
      "update_type": "EXPIRY_UPDATE",
      "subscription_id": "SUB-123456789ABC"
    }
  }'
```

Replace `SUB-123456789ABC` with an actual subscription ID from your database.
