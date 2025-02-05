#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install all the packages from the requirements file
pip install --upgrade pip
pip install -r requirements.txt

# Convert static asset files (for the admin interface)
python manage.py collectstatic --no-input

# Initialize the database
python manage.py makemigrations
python manage.py migrate