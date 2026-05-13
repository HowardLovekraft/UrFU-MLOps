from typing import Final

from fastapi import status
from fastapi.testclient import TestClient
from httpx import Response

from src.db import get_record
from src.schemas import RecordSchema, PredictionSchema


ENDPOINT_URL: Final = '/predict'


def test_valid_request(
    client: TestClient,
    valid_request: RecordSchema,
    valid_response: PredictionSchema
) -> None:
    response: Response =  client.post(ENDPOINT_URL, json=valid_request.model_dump())
    assert response.status_code == 200
    assert response.json() == valid_response.model_dump()


def test_invalid_enum_in_request(
    client: TestClient,
    request_with_invalid_enum: dict
) -> None:
    response: Response = client.post(ENDPOINT_URL, json=request_with_invalid_enum)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_db(
    client: TestClient,
    valid_request_2: RecordSchema
) -> None:
    assert get_record(valid_request_2) is None
    client.post(ENDPOINT_URL, json=valid_request_2.model_dump())
    assert isinstance(get_record(valid_request_2), int)
