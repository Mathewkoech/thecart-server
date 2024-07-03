#!/usr/bin/env bash

# Exit on error
set -o errexit

# Ensure venv exists and activate it
python3 -m venv venv
source venv/bin/activate

# Update and install necessary packages
apt-get update
apt-get install -y libxml2-dev libxslt1-dev build-essential libssl-dev

# Install Python dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Apply migrations
python manage.py migrate
