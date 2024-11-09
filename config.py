import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_dev_key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')  # Use DATABASE_URL from the environment
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
}