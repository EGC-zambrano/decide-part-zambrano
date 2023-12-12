#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

cd decide
cp local_settings.deploy.py local_settings.py
if [[ $CREATE_SUPERUSER ]]; 
then
    python manage.py createsuperuser --no-input
fi
python manage.py collectstatic --no-input
python manage.py makemigrations
python manage.py migrate

