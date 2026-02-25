FROM ghcr.io/astral-sh/uv:python:3.12-trixie-slim
WORKDIR /app
COPY . .
RUN uv sync
EXPOSE 5001
CMD ["uv", "run", "main.py"]
