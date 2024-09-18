FROM python:3.11-alpine

COPY . /docker_app
WORKDIR /docker_app
RUN apk add --no-cache gcc musl-dev linux-headers bash
RUN python -m pip install pipenv
RUN python -m pipenv install --deploy --ignore-pipfile
EXPOSE 9824

ENV DATABASE_URL="postgres://user:pass@landing.databases.leamaya.internal/domainAuth"

COPY ./big_bad.py /root/.local/share/virtualenvs/docker_app-LajRLmAI/lib/python3.11/site-packages/oidc_provider/migrations/0027_alter_client_id_alter_code_id_alter_responsetype_id_and_more.py

ENTRYPOINT /bin/bash -c "cd /docker_app && ./start.sh"
