# Card Freshness Management with PayPal Account Updater

This document provides instructions on how to manage the freshness of payment cards in your e-commerce system using PayPal's Account Updater service.

## Overview

Payment cards can expire or be replaced, leading to failed transactions and lost revenue. PayPal's Account Updater service helps keep card information up-to-date by automatically receiving updates from card networks when a customer's card details change.

## How It Works

1. **Subscribe Cards to PayPal AU Service**: When a customer adds a card to your system, you subscribe that card to PayPal's Account Updater service.
2. **Receive Updates via Webhooks**: PayPal sends webhook events when card details change (e.g., expiry date updates).
3. **Update Card Information**: Your system processes these webhook events and updates the card information in your database.

## Implementation Steps

### 1. Add Subscription ID to Cards Table

Each card in your database needs a `subscription_id` field to track its subscription with PayPal's Account Updater service.

```sql
ALTER TABLE cards ADD COLUMN subscription_id VARCHAR(100);
```

### 2. Subscribe Cards to PayPal AU Service

When a customer adds a new card, subscribe it to PayPal's Account Updater service:

```python
def subscribe_card_to_paypal_au(card_number, expiry_date):
    # Call PayPal API to create a subscription
    response = paypal_api.create_subscription(
        pan=card_number,
        expiry_date=expiry_date
    )
    
    # Extract the subscription ID from the response
    subscription_id = response.get('id')
    
    # Store the subscription ID with the card
    update_card_subscription_id(card_id, subscription_id)
    
    return subscription_id
```

### 3. Set Up Webhook Endpoint

Create a webhook endpoint to receive card update events from PayPal:

```python
@app.route('/webhooks/card-updated', methods=['POST'])
def webhook_card_updated():
    # Get the webhook payload
    payload = request.json
    
    # Extract the subscription ID and updated card information
    subscription_id = payload['resource']['subscription_id']
    new_expiry_date = payload['expiry_date']
    
    # Update the card in the database
    attributes = {'expiry_date': new_expiry_date}
    updated_card = update_card_by_subscription_id(subscription_id, attributes)
    
    if updated_card:
        return jsonify({"status": "success", "card": updated_card})
    else:
        return jsonify({"error": "Failed to update card"}), 500
```

### 4. Register Webhook with PayPal

Register your webhook endpoint with PayPal to receive card update events:

```python
def register_webhook():
    # Call PayPal API to register webhook
    response = paypal_api.create_webhook(
        url="https://your-domain.com/webhooks/card-updated",
        event_types=["CARD.UPDATED"]
    )
    
    # Store the webhook ID for future reference
    webhook_id = response.get('id')
    
    return webhook_id
```

## Testing

### 1. Add a Test Card with Subscription ID

```python
def add_test_card():
    # Generate a unique subscription ID
    subscription_id = f"SUB-TEST-{uuid.uuid4().hex[:8].upper()}"
    
    # Add a card with an expired date
    card = Card(
        user_id=user_id,
        card_number=encrypt_card_number("4111111111111111"),
        last_four="1111",
        expiry_date="2023-01",  # Expired date
        cardholder_name="Test User",
        card_type="Visa",
        subscription_id=subscription_id
    )
    
    # Save the card to the database
    db.session.add(card)
    db.session.commit()
    
    return card
```

### 2. Send a Test Webhook Event

```python
def test_webhook():
    # Create a test payload
    payload = {
        "expiry_date": "2032-01",  # New expiry date
        "resource": {
            "update_type": "EXPIRY_UPDATE",
            "subscription_id": "SUB-TEST-781157F1"  # Subscription ID of the test card
        }
    }
    
    # Send the webhook event
    response = requests.post(
        "http://localhost:8000/webhooks/card-updated",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    return response
```

### 3. Verify Card Update

```python
def verify_card_update(subscription_id):
    # Query the card with the given subscription ID
    card = Card.query.filter_by(subscription_id=subscription_id).first()
    
    if card:
        print(f"Card expiry date: {card.expiry_date}")
    else:
        print(f"No card found with subscription ID: {subscription_id}")
```

## Best Practices

1. **Secure Card Data**: Always encrypt card numbers and other sensitive data.
2. **Handle Webhook Failures**: Implement retry logic for failed webhook processing.
3. **Monitor Subscription Status**: Regularly check the status of card subscriptions.
4. **Update All Card Instances**: If a customer has multiple instances of the same card, update all of them.
5. **Notify Customers**: Consider notifying customers when their card information is updated.

## Troubleshooting

- **Webhook Not Received**: Verify that your webhook endpoint is publicly accessible and properly registered with PayPal.
- **Card Not Updated**: Check that the subscription ID in the webhook event matches a card in your database.
- **Subscription Failed**: Ensure that the card number and expiry date are valid when subscribing to the service.

## Conclusion

By implementing PayPal's Account Updater service, you can reduce payment failures due to expired or replaced cards, improving the customer experience and increasing revenue.
