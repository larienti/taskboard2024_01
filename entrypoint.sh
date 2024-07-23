#!/bin/sh

# Print current directory and its contents
echo "Current directory: $(pwd)"
ls -la

# Check if migrations directory exists
if [ -d "migrations" ]; then
    echo "Migrations directory exists"
else
    echo "Migrations directory does not exist"
fi

# Initialize migrations if they don't exist
if [ ! -d "migrations" ]; then
    echo "Initializing migrations"
    flask db init
fi

# Create a new migration (if there are changes)
echo "Creating new migration"
flask db migrate -m "Heroku migration"

# Apply the migration
echo "Applying migration"
flask db upgrade

# Start the application with gunicorn
echo "Starting gunicorn"
gunicorn --bind 0.0.0.0:$PORT run:app