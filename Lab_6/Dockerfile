FROM ghcr.io/astral-sh/uv:alpine3.23

WORKDIR /usr/src/app

COPY src/ tests/ pyproject.toml ./
RUN uv sync

CMD ["uv", "run", "fastapi"]
