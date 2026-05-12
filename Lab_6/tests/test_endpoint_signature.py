import requests
from typing import Final

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from src.app import app


ENDPOINT_URL: Final = 'http://'


@pytest.fixture(scope='session')
def web_app() -> FastAPI:
    return app


def test_request_signature(web_app: FastAPI):
   requests.post(url=ENDPOINT_URL, data=VALID_REQUEST)
