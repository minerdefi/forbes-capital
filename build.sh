#!/usr/bin/env bash
# exit on error
set -o errexit

echo "==> Starting Forbes Capital build process..."

# Install dependencies
echo "==> Installing Python dependencies..."
pip install -r requirements.txt

# Collect static files
echo "==> Collecting static files..."
python manage.py collectstatic --no-input --clear

# Apply database migrations
echo "==> Running database migrations..."
python manage.py migrate

echo "==> Build completed successfully!"