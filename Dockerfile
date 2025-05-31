ARG BASE_IMAGE=python:3.11-slim

FROM ${BASE_IMAGE}

RUN python3 -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install poetry

WORKDIR /app

COPY ./pyproject.toml ./poetry.lock /app/
RUN . /venv/bin/activate && /venv/bin/poetry install --no-root
COPY . /app/

ENTRYPOINT ["/venv/bin/python"]
