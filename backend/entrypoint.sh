#!/bin/sh
set -e

python manage.py makemigrations users objects inspections elements defects measurements reports dictionaries audit files notifications --noinput
python manage.py migrate --noinput
python manage.py runserver 0.0.0.0:8000

