import os

import os
from urllib.parse import urlparse

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_dev_key')
    
    # Parse DATABASE_URL components
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        url = urlparse(database_url)
        DB_USER = url.username
        DB_PASSWORD = url.password
        DB_HOST = url.hostname
        DB_PORT = url.port or 5432
        DB_NAME = url.path[1:]  # Remove leading '/'
        
        # Construct URL ensuring proper formatting
        SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    else:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.getenv('DB_POOL_SIZE', '5')),
        'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', '10')),
        'pool_timeout': int(os.getenv('DB_POOL_TIMEOUT', '30')),
        'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', '1800')),
    }

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False
    # Additional production settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    PREFERRED_URL_SCHEME = 'https'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
}