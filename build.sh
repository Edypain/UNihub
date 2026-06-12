#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Build tailwind using django-tailwind + pytailwindcss
python manage.py tailwind build

# Collect static files
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate

# Create superuser securely using environment variables if it doesn't exist
python manage.py shell -c "import os; from django.contrib.auth.models import User; username=os.environ.get('ADMIN_USERNAME', 'admin'); email=os.environ.get('ADMIN_EMAIL', 'admin@example.com'); password=os.environ.get('ADMIN_PASSWORD', 'YourPassword123'); User.objects.filter(username=username).exists() or User.objects.create_superuser(username, email, password)"

