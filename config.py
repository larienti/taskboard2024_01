import os
from urllib.parse import urlparse, parse_qsl, urlencode

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_secret_key'
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        url = urlparse(db_url)
        query = dict(parse_qsl(url.query))
        query.update({'sslmode': 'require', 'connect_timeout': '30'})
        url = url._replace(query=urlencode(query))
        SQLALCHEMY_DATABASE_URI = url.geturl()
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///your_database.db'
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