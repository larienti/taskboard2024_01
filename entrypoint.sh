#!/bin/bash

echo "Current directory: $(pwd)"
ls -la

# Display the database URL for debugging
echo "Database URL: $SQLALCHEMY_DATABASE_URI"

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL connection..."
until pg_isready -h postgres.railway.internal -p 5432 -U postgres; do
    >&2 echo "PostgreSQL is unavailable - retrying"
    sleep 5
done

echo "PostgreSQL is up - proceeding"

# Initialize migrations if not exists
if [ ! -d "migrations" ]; then
    echo "Initializing migrations"
    flask db init
fi

# Run migrations
echo "Creating new migration (if necessary)"
flask db migrate -m "Railway migration" || echo "No changes to migrate."

echo "Applying migrations"
flask db upgrade

# Start application with gunicorn
echo "Starting gunicorn"
exec gunicorn --bind 0.0.0.0:$PORT run:app