import logging
from app import create_app

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

try:
    logger.info("Starting Flask application...")
    app = create_app('dev')
    
    if __name__ == '__main__':
        logger.info("Running Flask server on http://0.0.0.0:5000")
        app.run(host='0.0.0.0', port=5000, debug=True)
except Exception as e:
    logger.error(f"Error starting Flask application: {e}")
    raise
