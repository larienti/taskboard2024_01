from app import create_app, db
from flask_migrate import Migrate

app = create_app('production')  # or use 'development' for local development

if __name__ == '__main__':
    app.run()