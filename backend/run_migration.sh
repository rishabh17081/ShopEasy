#!/bin/bash

# Run the migration to add the unique constraint to subscription_id
cd "$(dirname "$0")"
export PYTHONPATH=$PYTHONPATH:$(pwd)

echo "Running migration to add unique constraint to subscription_id..."
python3 -m flask db upgrade

echo "Migration completed."
