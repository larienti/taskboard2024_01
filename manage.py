from flask_migrate import Migrate
from flask_script import Manager
from app import create_app, db

app = create_app()
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run()