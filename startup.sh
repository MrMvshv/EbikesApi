#!/bin/bash
chmod +x start.sh
cd /var/task && exec gunicorn EBARestAPIServer.wsgi:application --bind 0.0.0.0:8000 --workers 2 --threads 1 --timeout 120