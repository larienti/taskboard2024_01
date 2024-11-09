#!/bin/bash
set -e  # Exit on error

echo "Starting deployment process..."
echo "Current directory: $(pwd)"
ls -la

# Parse the DATABASE_URL to get connection details
if [ -n "$DATABASE_URL" ]; then
    echo "Database URL is set"
    # Extract host from DATABASE_URL (assumes PostgreSQL URL format)
    DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\).*/\1/p')
    echo "Database host: $DB_HOST"
else
    echo "WARNING: DATABASE_URL is not set!"
fi

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL connection..."
max_retries=30
counter=0
until pg_isready -h $DB_HOST -p 5432; do
    counter=$((counter + 1))
    if [ $counter -gt $max_retries ]; then
        echo "Failed to connect to PostgreSQL after $max_retries attempts."
        exit 1
    fi
    >&2 echo "PostgreSQL is unavailable - sleeping 5 seconds (attempt $counter/$max_retries)"
    sleep 5
done

echo "PostgreSQL is up - proceeding with deployment"

# Initialize migrations directory if it doesn't exist
if [ ! -d "migrations" ]; then
    echo "Initializing migrations directory..."
    flask db init
    echo "Migrations directory initialized"
fi

# Run database migrations
echo "Running database migrations..."
flask db migrate -m "Railway deployment migration" || echo "No new migrations needed"
flask db upgrade
echo "Database migrations completed"

# Start Gunicorn with appropriate settings
echo "Starting Gunicorn server..."
exec gunicorn \
    --bind 0.0.0.0:${PORT:-5000} \
    --workers=4 \
    --threads=2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    run:app