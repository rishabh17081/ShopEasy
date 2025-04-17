#!/bin/bash

# Activate the virtual environment
source venv/bin/activate
pip3 install -r requirements.txt
# Set Flask environment variables
export FLASK_APP=app
export FLASK_ENV=development

# Run the Flask development server
flask run --host=0.0.0.0 --port=5001
