FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    INFOFLOW_DB_PATH=/data/infoflow.db

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends graphviz \
    && rm -rf /var/lib/apt/lists/*

# Unprivileged account to run as. /data is the only path the app needs to write:
# mount its own SQLite file there, nothing else.
RUN useradd --system --uid 10001 --user-group --no-create-home infoflow \
    && install -d -o infoflow -g infoflow /data

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache uv sync --frozen --no-dev --no-install-project
COPY . .
RUN --mount=type=cache,target=/root/.cache uv sync --frozen --no-dev \
    && chown -R infoflow:infoflow /app

USER infoflow
EXPOSE 5001
# Run the venv interpreter directly: no dev reloader, and no uv writes at runtime.
CMD ["/app/.venv/bin/python", "main.py"]
