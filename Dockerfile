ARG BASE_IMAGE=python:3.11-slim
ARG WORKDIR=/app

FROM ${BASE_IMAGE}

ARG WORKDIR

RUN python3 -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install poetry

COPY ./pyproject.toml ./poetry.lock ${WORKDIR}/
RUN . /venv/bin/activate && /venv/bin/poetry install --no-root
COPY . ${WORKDIR}/

ENTRYPOINT ["/venv/bin/python"]

LABEL org.opencontainers.image.source=https://github.com/jinglemansweep/rag-actions
