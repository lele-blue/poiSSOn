#!/bin/bash

rm -r staticfiles
python -m pipenv run python manage.py collectstatic
python -m pipenv run python manage.py migrate
python -m pipenv run gunicorn domainAuth.wsgi -b :80 --log-file -
