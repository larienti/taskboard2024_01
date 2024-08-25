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
        config_name = os.environ.get('FLASK_ENV', 'default')

    app = Flask(__name__, static_folder='static', static_url_path='/static')
    app.config.from_object(config[config_name])

    db.init_app(app)
    login_manager.init_app(app)
    Migrate(app, db)

    from .routes import main
    app.register_blueprint(main)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    return app