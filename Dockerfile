FROM python:3.11-alpine

COPY . /docker_app
WORKDIR /docker_app
RUN apk add --no-cache gcc musl-dev linux-headers bash
RUN python -m pip install pipenv
RUN python -m pipenv install --deploy --ignore-pipfile
EXPOSE 9824

ENV DATABASE_URL="postgres://user:pass@landing.databases.leamaya.internal/domainAuth"

ENTRYPOINT /bin/bash -c "cd /docker_app && ./start.sh"
