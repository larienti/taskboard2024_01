#!/bin/sh

# Wait for the database to be ready
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "db" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 5
done

>&2 echo "Postgres is up - executing command"

# Remove existing migrations
rm -rf migrations

# Initialize migrations
flask db init

# Create a new migration
flask db migrate -m "Create tables"

# Apply the migration
flask db upgrade

# Start the Flask application
python run.py