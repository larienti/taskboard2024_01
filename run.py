from app import create_app, db
from flask_migrate import Migrate

app = create_app()
migrate = Migrate(app, db, directory=os.path.join(os.path.dirname(__file__), 'migrations'))

if __name__ == '__main__':
    app.run()
    #app.run(debug=True, host='0.0.0.0', port=5000)