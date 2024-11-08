import time
import psycopg2
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import config
import os

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'production')  # Default to production

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    print(f"Environment: {config_name}")
    print(f"SQLALCHEMY_DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

    # Retry connection to the database with psycopg2
    retries = 5
    while retries > 0:
        try:
            # Test connection using psycopg2
            conn = psycopg2.connect(app.config['SQLALCHEMY_DATABASE_URI'])
            conn.close()
            print("Successfully connected to the database!")
            break
        except psycopg2.OperationalError as e:
            print(f"Database connection failed: {e}")
            retries -= 1
            time.sleep(5)  # wait 5 seconds before retrying
    else:
        print("Could not connect to the database after several attempts.")

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    Migrate(app, db)

    # Register Blueprints
    from .routes import main
    app.register_blueprint(main)

    # User loader callback for Flask-Login
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    return app