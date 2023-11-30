#!/bin/bash

echo "WE ARE IN ENTRYSCRIPT"
pwd

python manage.py migrate
echo "MIGRATIONS COMPLITED"

python manage.py collectstatic
echo "SINGLE STATICFILE COLLECTED"

gunicorn stock.wsgi:application --bind 0.0.0.0:8000 --log-level debug --workers 1 --timeout 90