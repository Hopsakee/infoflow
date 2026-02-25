FROM ghcr.io/astral-sh/uv:python:3.12-trixie-slim
WORKDIR /app
COPY . .
RUN --mount=type=cache,target=/root/.cache uv sync
EXPOSE 5001
CMD ["uv", "run", "main.py"]
