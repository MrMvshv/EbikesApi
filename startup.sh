#!/bin/bash
chmod +x startup.sh
python3 manage.py migrate && python manage.py collectstatic && gunicorn EBARestAPIServer.wsgi:application --bind 0.0.0.0:8000 --workers 2