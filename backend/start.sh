#!/bin/bash
cd foodgram && \
python manage.py migrate --noinput && \
python manage.py collectstatic --noinput && \
gunicorn -w 3 -b 0.0.0.0:8000 foodgram.wsgi:application