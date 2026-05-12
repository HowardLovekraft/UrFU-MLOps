from fastapi.testclient import TestClient
import pytest

from src.app import app
from src.schemas import PredictionSchema, RecordSchema


@pytest.fixture(scope='session')
def client() -> TestClient:
    """Клиент API для юнит-тестов."""
    return TestClient(app)


@pytest.fixture(scope='session')
def valid_request() -> RecordSchema:
    """Валидный запрос к модели."""
    return RecordSchema(
        period='3rd Period',
        subject='Biology',
        co2_ppm=663.4,
        pm25_ugm3=8.07,
        temperature_c=21.9,
        humidity_pct=46.0,
        reaction_time_ms=213,
        focus_rating=7.2,
        error_rate=1.68,
        heart_rate_bpm=75,
        cognitive_impairment=0.0191,
        air_quality=2
    )


@pytest.fixture(scope='session')
def valid_response() -> PredictionSchema:
    return PredictionSchema(
        performance_index=1
    )
