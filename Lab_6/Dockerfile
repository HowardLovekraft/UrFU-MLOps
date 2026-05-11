FROM python:3.13

WORKDIR /usr/src/app

COPY . .
RUN uv sync

CMD ["uv", "app.py"]
