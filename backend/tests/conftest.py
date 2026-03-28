import asyncio
from collections.abc import AsyncGenerator, Generator
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.deps import get_db, get_current_patient, get_current_staff, get_redis, get_event_bus

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_db_session() -> AsyncMock:
    """Provide a mocked SQLAlchemy AsyncSession."""
    session = AsyncMock()
    # Mock commonly used methods
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.refresh = AsyncMock()
    return session

@pytest.fixture
def mock_redis() -> AsyncMock:
    """Provide a mocked Redis client."""
    client = AsyncMock()
    return client

@pytest.fixture
def mock_event_bus() -> AsyncMock:
    """Provide a mocked EventBus."""
    bus = AsyncMock()
    bus.publish = AsyncMock()
    return bus

@pytest.fixture
async def async_client(
    mock_db_session: AsyncMock,
    mock_redis: AsyncMock,
    mock_event_bus: AsyncMock
) -> AsyncGenerator[AsyncClient, None]:
    """Provide an asynchronous httpx client for endpoint testing."""
    
    # Override dependencies
    app.dependency_overrides[get_db] = lambda: mock_db_session
    app.dependency_overrides[get_redis] = lambda: mock_redis
    app.dependency_overrides[get_event_bus] = lambda: mock_event_bus
    
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
        
    app.dependency_overrides.clear()

@pytest.fixture
def mock_patient_auth():
    """Mock the patient authentication dependency."""
    def _override():
        return {
            "patient_id": "00000000-0000-0000-0000-000000000001",
            "role": "patient",
            "site_id": "00000000-0000-0000-0000-000000000002",
        }
    app.dependency_overrides[get_current_patient] = _override
    yield
    app.dependency_overrides.pop(get_current_patient, None)

@pytest.fixture
def mock_crc_auth():
    """Mock the CRC staff authentication dependency."""
    def _override():
        return {
            "staff_id": "00000000-0000-0000-0000-000000000003",
            "role": "crc",
            "sites": ["00000000-0000-0000-0000-000000000002"]
        }
    app.dependency_overrides[get_current_staff] = _override
    yield
    app.dependency_overrides.pop(get_current_staff, None)
