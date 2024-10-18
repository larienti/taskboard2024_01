import os
from urllib.parse import urlparse, urlencode

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_secret_key'
    db_url = os.environ.get('DATABASE_PUBLIC_URL')
    if db_url:
        url = urlparse(db_url)
        query = dict(urlparse.parse_qsl(url.query))
        query.update({'connect_timeout': '10'})
        url = url._replace(query=urlencode(query))
        SQLALCHEMY_DATABASE_URI = url.geturl()
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///your_database.db'  # Fallback to SQLite
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