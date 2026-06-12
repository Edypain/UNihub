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

# Set a fallback SECRET_KEY and dummy CLOUDINARY_URL for build commands
ENV SECRET_KEY=django-insecure-build-fallback
ENV CLOUDINARY_URL=cloudinary://dummy:dummy@dummy

# Build tailwind styles and collect static files
RUN python manage.py tailwind build \
    && python manage.py collectstatic --no-input

# Make the start script executable
RUN chmod +x /app/start.sh

# Expose the application port
EXPOSE 8000

# Start the application using the start script
CMD ["/app/start.sh"]

