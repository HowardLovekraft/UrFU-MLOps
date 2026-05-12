FROM python:3.13

WORKDIR /usr/src/app

COPY src/ tests/ pyproject.toml ./
RUN uv sync

CMD ["uv", "src/app.py"]
