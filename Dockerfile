# Use an explicit, slim Python base image for speed and size reduction
FROM python:3.12-slim

# Prevent Python from writing .pyc files and force unbuffered logging for clean logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establish the working directory inside the container
WORKDIR /app

# Install system dependencies required for database compilation adapters
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install packages
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the remaining application source files
COPY . /app/

# Expose the application port
EXPOSE 8000

# Execute file collection, push database migrations, and boot up Gunicorn
CMD ["sh", "-c", "python manage.py collectstatic --noinput && python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:8000"]