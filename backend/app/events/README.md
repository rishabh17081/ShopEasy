# PayPal Account Updater Integration

This directory contains the implementation for PayPal's Account Updater service which helps keep payment card information up-to-date in the merchant database.

## Overview

When a customer's card details change (e.g., expiry date updates, card reissue), the PayPal Account Updater service will detect these changes and send webhook notifications to your application. This integration allows ShopEasy to automatically update stored card information, reducing failed transactions and improving the customer experience.

## How It Works

1. **Card Subscription**: When a payment card is added to the system, it is subscribed to PayPal's Account Updater service. The subscription ID is stored in the database along with the card details.

2. **Webhook Events**: PayPal sends webhook events to the `/api/webhooks/paypal/account-updater` endpoint when card information changes.

3. **Card Updates**: The webhook handler processes the event, extracts the updated card information, and updates the corresponding card in the database using the subscription ID.

## Files

- `paypal_webhook.py`: Contains the implementation for processing PayPal webhook events
- `merchant_db_connector.py`: Database connector that includes methods to update card information

## Configuration

The webhook integration requires a PayPal webhook secret for secure verification. In production, this should be set in the environment variables:

```bash
export PAYPAL_WEBHOOK_SECRET="your-webhook-secret"
```

In development mode, signature verification can be skipped for testing by setting:

```bash
export SKIP_WEBHOOK_VERIFICATION="true"
```

## Testing

To test the webhook locally, you can use PayPal's Webhook Simulator or tools like ngrok to expose your local server to the internet.

Example webhook event payload:

```json
{
  "id": "WH-3G395883RX430412N-5WM67990UE1072645",
  "event_type": "PAYMENT.ACCOUNT-STATUS.UPDATED",
  "resource": {
    "id": "SUB-3AA78323A5",
    "expiry": {
      "month": 3,
      "year": 2028
    }
  }
}
```

## Implementation Notes

- All webhook events are securely verified using HMAC-SHA256 signatures
- Card updates are logged for auditing purposes
- The system handles various formats of expiry dates to ensure compatibility
