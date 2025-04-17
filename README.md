# E-Commerce Platform

## Card Freshness Management

### PayPal Account Updater Service

The platform integrates PayPal's Account Updater service to maintain up-to-date payment card information. This feature helps prevent payment failures due to outdated card details.

#### Key Features

- **Automatic Card Updates**: Tracks changes in card information such as:
  - Expiration dates
  - Reissued card numbers
  - Account status changes

- **Subscription-based Tracking**: Each card can be subscribed to PayPal's update service
  - Unique subscription ID stored with each card
  - Webhooks receive real-time updates

#### How It Works

1. **Card Subscription**
   - When a card is added, it can be subscribed to the PayPal Account Updater
   - Uses PayPal's API to create a subscription for the card
   - Stores the subscription ID in the database

2. **Webhook Processing**
   - Receives webhook events from PayPal about card changes
   - Automatically updates the card information in the database
   - Logs all update events for tracking

#### Configuration

Set up the following environment variables in `.env`:
- `PAYPAL_CLIENT_ID`: PayPal API Client ID
- `PAYPAL_CLIENT_SECRET`: PayPal API Client Secret
- `PAYPAL_WEBHOOK_URL`: Endpoint for receiving PayPal webhook events

#### API Endpoints

- `POST /api/paypal/create_subscription`: Create a subscription for a card
- `GET /api/cards/subscription`: Retrieve a card's subscription details
- `POST /api/cards/update_subscription`: Manually update a card's subscription ID

### Benefits

- Reduce payment failures
- Minimize manual card information updates
- Improve payment success rates
- Enhance user experience

## Setup

1. Install dependencies
2. Configure environment variables
3. Run database migrations
4. Start the application

## Contributing

Please read our contributing guidelines before submitting pull requests.
