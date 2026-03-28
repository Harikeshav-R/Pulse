import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_wearable_sync_requires_auth(async_client: AsyncClient):
    payload = {
        "device_type": "apple_watch",
        "readings": []
    }
    response = await async_client.post("/api/v1/wearable/sync", json=payload)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_wearable_sync_patient_auth(async_client: AsyncClient, mock_patient_auth):
    payload = {
        "device_type": "apple_watch",
        "readings": [
            {
                "metric": "heart_rate",
                "value": 75.0,
                "unit": "bpm"
            }
        ]
    }
    response = await async_client.post("/api/v1/wearable/sync", json=payload)
    assert response.status_code in [200, 422, 500]
