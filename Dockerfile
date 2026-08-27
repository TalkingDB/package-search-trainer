FROM python:3.13-slim-bookworm

RUN apt-get update && apt-get install -y curl
RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app
COPY pyproject.toml poetry.lock ./

RUN --mount=type=cache,target=/root/.cache/pypoetry \
    --mount=type=cache,target=/root/.cache/pip \
    poetry config virtualenvs.create false && poetry lock && poetry install --no-root --no-interaction --no-ansi --only main

COPY ./talkingdb_st /app/talkingdb_st

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

EXPOSE 8095

CMD ["poetry", "run", "uvicorn", "talkingdb_st.main:app", "--host", "0.0.0.0", "--port", "8095", "--workers", "1", "--loop", "uvloop", "--http", "httptools"]
