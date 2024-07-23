#!/bin/sh

# Wait for the database to be ready
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "db" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 5
done

>&2 echo "Postgres is up - executing command"
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