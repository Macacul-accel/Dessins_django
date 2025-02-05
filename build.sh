#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install all the packages from the requirements file
pip install --upgrade pip && -r requirements.txt

# Initialize the database
python manage.py migrate