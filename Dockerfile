ARG BASE_IMAGE=python:3.11-slim

FROM ${BASE_IMAGE}
LABEL org.opencontainers.image.source=https://github.com/jinglemansweep/rag-actions

RUN mkdir -p /app && \
    python3 -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install poetry

COPY ./entrypoint.sh /entrypoint.sh
COPY ./pyproject.toml ./poetry.lock /app/
RUN . /venv/bin/activate && cd /app/ && /venv/bin/poetry install --no-root
COPY . /app/

ENTRYPOINT ["/bin/sh", "/entrypoint.sh"]
