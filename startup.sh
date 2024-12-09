#!/bin/bash
python3 manage.py migrate && python3 manage.py collectstatic && gunicorn EBARestAPIServer.wsgi --workers 2