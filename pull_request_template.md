# PayPal Account Updater Webhook Implementation

## Description
This PR adds a webhook implementation for the PayPal Account Updater service to automatically update card information when changes are detected by PayPal.

## Changes
- Added FastAPI endpoint at `/webhooks/card-updated` to receive PayPal notifications
- Implemented card lookup and update logic based on subscription IDs
- Added fallback mechanisms for finding cards by subscription ID when direct updates fail
- Added comprehensive logging for troubleshooting

## How to Test
1. Start the FastAPI server: `uvicorn backend.app.events.webhook_card_update:app --reload`
2. Send a test webhook payload to `http://localhost:8000/webhooks/card-updated`:
```json
{
  "event_type": "ACCOUNT_STATUS.UPDATED",
  "resource": {
    "subscription_id": "[YOUR_SUBSCRIPTION_ID]",
    "updated_details": {
      "expiry_date": "2030-12"
    }
  }
}
```
3. Check that the corresponding card's expiry date is updated in the database

## Deployment Instructions
1. Deploy the FastAPI application to your webhook server
2. Update your PayPal Account Updater configuration to point to the new webhook URL
3. Monitor webhook events in the server logs to ensure proper functioning

## Additional Notes
- The implementation follows patterns from the reference implementation in the MCP connector project
- Error handling includes retry mechanisms and detailed logging for troubleshooting
- All cards should be subscribed to PayPal Account Updater with the `create_subscription` API before using this webhook
