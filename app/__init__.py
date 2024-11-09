import time
import psycopg2
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from app.config import config
import os
import logging

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'production')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting application in {config_name} mode")
    logger.info(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI'].split('@')[0]}@***")

    # Enhanced database connection retry logic
    max_retries = 5
    retry_count = 0
    retry_delay = 5  # seconds

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
    migrate = Migrate(app, db)

    # Register Blueprints
    from .routes import main
    app.register_blueprint(main)

    # User loader callback
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Add health check endpoint
    @app.route('/health')
    def health_check():
        try:
            db.session.execute('SELECT 1')
            return {'status': 'healthy'}, 200
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {'status': 'unhealthy', 'error': str(e)}, 500

    return app