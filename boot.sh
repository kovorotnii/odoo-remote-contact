#!/bin/sh
#exec gunicorn --bind 0.0.0.0:5000 main:app
exec gunicorn -c config.py --log-level=debug app:app
