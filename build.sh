#!/bin/bash
# Exit on error
set -o errexit

# Install all the packages from the requirements file
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Initialize the database
python manage.py makemigrations
python manage.py migrate