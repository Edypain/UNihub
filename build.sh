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
