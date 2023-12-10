#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python decide/manage.py collectstatic --no-input
python decide/manage.py migrate