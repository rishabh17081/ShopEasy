import os
from datetime import timedelta

class Config:
    # Basic configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-for-testing'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'ecommerce.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-dev'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # PayPal configuration
    PAYPAL_WEBHOOK_SECRET = os.environ.get('PAYPAL_WEBHOOK_SECRET') or 'paypal-webhook-secret-dev'
    
class DevelopmentConfig(Config):
    DEBUG = True
    # In development, we can skip webhook signature verification for testing
    SKIP_WEBHOOK_VERIFICATION = os.environ.get('SKIP_WEBHOOK_VERIFICATION', 'True').lower() == 'true'
    
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    # Always skip verification in tests
    SKIP_WEBHOOK_VERIFICATION = True
    
class ProductionConfig(Config):
    DEBUG = False
    # Never skip verification in production
    SKIP_WEBHOOK_VERIFICATION = False
    
config_by_name = {
    'dev': DevelopmentConfig,
    'test': TestingConfig,
    'prod': ProductionConfig
}
