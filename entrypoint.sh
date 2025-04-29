#!/bin/sh

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
while ! nc -z $DB_HOST $DB_PORT; do
    sleep 0.1
done
echo "PostgreSQL started"

# Wait for Redis
echo "Waiting for Redis..."
while ! nc -z $REDIS_HOST 6379; do
    sleep 0.1
done
echo "Redis started"

# Wait for RabbitMQ
echo "Waiting for RabbitMQ..."
while ! nc -z $RABBITMQ_HOST 5672; do
    sleep 0.1
done
echo "RabbitMQ started"

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start the application
echo "Starting application..."
exec "$@" 