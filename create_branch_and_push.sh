#!/bin/bash
set -e

cd /Users/rishabhsharma/PycharmProjects/ecommerce-site

# Create and checkout a new branch
git checkout -b webhook-changes

# Add the new file
git add backend/app/events/webhook_card_update.py

# Commit the changes
git commit -m "Add PayPal Account Updater webhook implementation"

# Push to GitHub
git push upstream webhook-changes
