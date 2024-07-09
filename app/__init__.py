from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'  # Change this!
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db/taskboard'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    from .routes import main
    from .models import User, Task
    app.register_blueprint(main)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    return app