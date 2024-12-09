#!/bin/bash
chmod +x startup.sh
python3 manage.py migrate && python manage.py collectstatic && gunicorn EBARestAPIServer.wsgi --workers 2