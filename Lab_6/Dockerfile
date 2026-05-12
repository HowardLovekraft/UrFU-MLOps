FROM ghcr.io/astral-sh/uv:debian-slim

WORKDIR /usr/src/Lab_6

COPY pyproject.toml ./
RUN uv sync
COPY . ./

ENV PYTHONPATH=/usr/src/Lab_6
EXPOSE 8000

CMD ["uv", "run", "src/app.py"]
