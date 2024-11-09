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
        raise ValueError("Invalid DATABASE_URL format. Must include scheme, username, password, and hostname")
    
    return True

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'production')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting application in {config_name} mode")
    
    # Verify database URL
    try:
        verify_db_url(app.config['SQLALCHEMY_DATABASE_URI'])
        parsed_url = urlparse(app.config['SQLALCHEMY_DATABASE_URI'])
        logger.info("Database connection details:")
        logger.info(f"  Host: {parsed_url.hostname}")
        logger.info(f"  Port: {parsed_url.port or 5432}")
        logger.info(f"  Database: {parsed_url.path[1:] if parsed_url.path else 'default'}")
        logger.info(f"  User: {parsed_url.username}")
    except Exception as e:
        logger.error(f"Database URL verification failed: {str(e)}")
        raise

    # Enhanced database connection retry logic
    max_retries = 5
    retry_count = 0
    retry_delay = 5

    while retry_count < max_retries:
        try:
            conn = psycopg2.connect(
                app.config['SQLALCHEMY_DATABASE_URI'],
                connect_timeout=5
            )
            conn.close()
            logger.info("Successfully connected to the database!")
            break
        except psycopg2.OperationalError as e:
            retry_count += 1
            logger.warning(f"Database connection attempt {retry_count}/{max_retries} failed: {str(e)}")
            
            if retry_count == max_retries:
                logger.error("Failed to connect to the database after maximum retries")
                raise
            
            time.sleep(retry_delay)
            retry_delay *= 1.5  # Exponential backoff

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    Migrate(app, db)

    # Register blueprints
    from .routes import main
    app.register_blueprint(main)

    # Define test route to check database connection
    @app.route('/test-db')
    def test_db():
        try:
            # Try raw psycopg2 connection
            conn = psycopg2.connect(
                dbname="railway",
                user="postgres",
                password="UvVNaBnMprSeoBhjIVolZzExVXKGiqAA",
                host="postgres.railway.internal",
                port="5432"
            )
            conn.close()
            
            # Then try SQLAlchemy
            db.session.execute('SELECT 1')
            db.session.commit()
            
            return {
                'status': 'success',
                'message': 'Database connection successful',
                'config': {
                    'host': app.config['SQLALCHEMY_DATABASE_URI'].split('@')[1].split('/')[0],
                    'database': app.config['SQLALCHEMY_DATABASE_URI'].split('/')[-1],
                    'user': 'postgres'
                }
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'uri': app.config['SQLALCHEMY_DATABASE_URI'].replace(
                    app.config.get('DB_PASSWORD', ''), '***'
                )
            }, 500

    return app