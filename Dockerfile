FROM python:3.11-alpine

RUN apk add --no-cache gcc musl-dev linux-headers npm bash && python -m pip install pipenv

WORKDIR /docker_app
COPY Pipfile Pipfile.lock /docker_app/
COPY src/package.json src/package-lock.json /docker_app/src/
RUN python -m pipenv install --deploy --ignore-pipfile && cd src && npm ci

COPY ./src/ /docker_app/src

RUN cd src && npm run build

COPY . /docker_app


ENTRYPOINT /bin/bash -c "cd /docker_app && ./start.sh"
