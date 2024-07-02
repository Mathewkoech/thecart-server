#!/usr/bin/env bash

# Exit on error
set -o errexit

# Ensure venv exists and activate it
python3.11 -m venv venv
source venv/bin/activate

rm -rf /var/lib/apt/lists/*
# Update and install necessary packages
# apt-get update
# apt-get install -y build-essential libssl-dev

# Install Python dependencies
pip install -r requirements.txt

# Collect static files
python3.11 manage.py collectstatic --no-input

# Apply migrations
python3.11 manage.py migrate
