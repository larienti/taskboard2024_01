FROM python:3.9.16-slim

# Install PostgreSQL client and other necessary packages
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Make sure the entrypoint script is executable
COPY entrypoint.sh .
RUN chmod +x /app/entrypoint.sh

# Use gunicorn as the production server
#CMD gunicorn --bind 0.0.0.0:$PORT run:app   
CMD ["/app/entrypoint.sh"]

FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Execute entrypoint script
CMD ["./entrypoint.sh"]