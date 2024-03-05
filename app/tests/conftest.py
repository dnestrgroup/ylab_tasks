import asyncio
from datetime import timedelta
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient

from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://localhost:8000/api/v1") as ac:
        yield ac


@pytest.mark.usefixtures("client")
class TestClientBase:
    @pytest.fixture(autouse=True)
    def get_client(self, client: AsyncClient) -> None:
        self.client = client