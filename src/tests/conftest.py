from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlmodel.ext.asyncio.session import AsyncSession

from src import app
from src.auth import router as auth_routes
from src.auth.dependencies import get_current_user
from src.auth.service import UserService
from src.books import routes as book_routes
from src.books.service import BookService
from src.db.main import get_session


@pytest.fixture
def fake_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def test_client(fake_session):
    previous_overrides = app.dependency_overrides.copy()

    async def override_session():
        yield fake_session

    app.dependency_overrides[get_session] = override_session
    try:
        with TestClient(
            app, base_url="http://localhost", raise_server_exceptions=False
        ) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)


@pytest.fixture
def authenticated_user(test_client):
    user = SimpleNamespace(uid=uuid4(), is_verified=True, role="user")

    async def override_user():
        return user

    async def override_token():
        return {"user": {"user_uid": str(user.uid)}}

    app.dependency_overrides[get_current_user] = override_user
    app.dependency_overrides[book_routes.access_token_bearer] = override_token
    return user


@pytest.fixture
def fake_users(monkeypatch):
    service = AsyncMock(spec=UserService)
    service.exist_user.return_value = False
    service.Create_user.return_value = SimpleNamespace(
        uid=uuid4(), Email="reader@example.com"
    )
    monkeypatch.setattr(auth_routes, "user_service", service)
    monkeypatch.setattr(auth_routes.send_email, "delay", Mock())
    return service


@pytest.fixture
def fake_book_service(monkeypatch):
    service = AsyncMock(spec=BookService)
    monkeypatch.setattr(book_routes, "book_service", service)
    return service
