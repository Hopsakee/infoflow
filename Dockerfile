FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim
WORKDIR /app
RUN apt update && apt install -y graphviz
COPY pyproject.toml uv.lock .
RUN --mount=type=cache,target=/root/.cache uv sync --no-install-project
COPY . .
RUN --mount=type=cache,target=/root/.cache uv sync
EXPOSE 5001
CMD ["uv", "run", "main.py"]
