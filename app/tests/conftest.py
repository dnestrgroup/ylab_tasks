import asyncio
from typing import Any, AsyncGenerator, Generator

import pytest
from httpx import AsyncClient

from app.main import app


@pytest.fixture(scope='session')  # type: ignore
def event_loop() -> Generator[Any, Any, Any]:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='function')  # type: ignore
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url='http://localhost:8000/api/v1') as ac:
        yield ac


@pytest.mark.usefixtures('client')
class TestClientBase:
    @pytest.fixture(autouse=True)  # type: ignore
    def get_client(self, client: AsyncClient) -> None:
        self.client = client
