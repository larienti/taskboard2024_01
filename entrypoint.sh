#!/bin/sh

# Initialize migrations if they don't exist
if [ ! -d "migrations" ]; then
    flask db init
fi

# Create a new migration (if there are changes)
flask db migrate -m "Heroku migration"

# Apply the migration
flask db upgrade

# Start the application with gunicorn
gunicorn --bind 0.0.0.0:$PORT run:app