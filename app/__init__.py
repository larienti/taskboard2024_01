import time
import psycopg2
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from app.config import config
import os
import logging
from urllib.parse import urlparse

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'

def verify_db_url(url):
    if not url:
        raise ValueError("DATABASE_URL is not set")
    
    parsed = urlparse(url)
    if not all([parsed.scheme, parsed.username, parsed.password, parsed.hostname]):
        raise ValueError("Invalid DATABASE_URL format. Must include scheme, username, password, and