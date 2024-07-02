#!/usr/bin/env bash
# Exit on error
python3.10 -m venv venv
source venv/bin/activate
set -o errexit
apt-get update
apt-get install -y build-essential libssl-dev

# Modify this line as needed for your package manager (pip, poetry, etc.)
pip install -r requirements.txt

# Convert static asset files
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py migrate