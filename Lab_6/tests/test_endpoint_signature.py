from typing import Final

from fastapi.testclient import TestClient
from httpx import Response

from src.schemas import RecordSchema, PredictionSchema


ENDPOINT_URL: Final = '/predict'


def test_endpoint_signature(
    client: TestClient,
    valid_request: RecordSchema,
    valid_response: PredictionSchema
) -> None:
    response: Response =  client.post(ENDPOINT_URL, json=valid_request.model_dump())
    assert response.status_code == 200
    assert response.json() == valid_response.model_dump()
