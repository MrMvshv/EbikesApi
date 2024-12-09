#!/bin/bash
chmod +x startup.sh
gunicorn EBARestAPIServer.wsgi:application --bind 0.0.0.0:8000 --workers 2