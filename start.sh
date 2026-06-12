#!/usr/bin/env bash
# exit on error
set -o errexit

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Create superuser securely using environment variables if it doesn't exist
echo "Creating superuser if it doesn't exist..."
python manage.py shell -c "import os; from django.contrib.auth.models import User; username=os.environ.get('ADMIN_USERNAME', 'admin'); email=os.environ.get('ADMIN_EMAIL', 'admin@example.com'); password=os.environ.get('ADMIN_PASSWORD', 'YourPassword123'); User.objects.filter(username=username).exists() or User.objects.create_superuser(username, email, password)"

# Start Gunicorn server
echo "Starting Gunicorn server..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000
