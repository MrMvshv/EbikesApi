#!/bin/bash
chmod +x startup.sh
python manage.py migrate && python manage.py collectstatic && gunicorn --workers 2 EBARestAPIServer.wsgi:application --bind 0.0.0.0:8000 --threads 1 --timeout 120 --access-logfile '-'  --error-logfile '-' 