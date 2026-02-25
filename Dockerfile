FROM ghcr.io/astral-sh/uv:python:3.12-trixie-slim
WORKDIR /app
COPY . .
RUN uv sync
CMD ["uv", "run", "main.py"]
