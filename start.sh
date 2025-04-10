#!/bin/bash

rm -r staticfiles
python -m pipenv run python manage.py collectstatic
python -m pipenv run python manage.py migrate
python -m pipenv run python manage.py setup_core_settings
python -m pipenv run gunicorn domainAuth.wsgi -b :80 --log-file - # &
# P_DJANGO=$!
# python -m pipenv run python ws_proxy.py &
# P_WSPROXY=$!
# wait $P_DJANGO $P_WSPROXY

