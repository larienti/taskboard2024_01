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

    # Attempt connection to the database
    try:
        with app.app_context():
            db.engine.connect()
        print("Successfully connected to the database!")
    except Exception as e:
        print(f"Failed to connect to the database: {str(e)}")

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