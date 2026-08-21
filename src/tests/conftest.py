from src.db.main import get_session
from src import app
from datetime import datetime
import uuid
from src.books.schemas import Book
from src.auth.dependencies import RefreshTokenBearer,RoleChecker,AccessTokenBearer 
from unittest.mock import Mock
from fastapi.testclient import TestClient
import pytest

mock_session=Mock()
mock_user_service=Mock()
mock_books_service=Mock()


def get_mock_session():
    yield mock_session


acces_token_bearer=AccessTokenBearer()
refresh_token_bearer=RefreshTokenBearer()
role_checker=RoleChecker("admin")

app.dependency_overrides[get_session]=get_mock_session    
app.dependency_overrides[role_checker]=Mock()
app.dependency_overrides[refresh_token_bearer]=Mock()

@pytest.fixture
def fake_session():
    return mock_session()


@pytest.fixture
def fake_users():
    return mock_session()

@pytest.fixture
def fake_book_service():
    return mock_books_service()

@pytest.fixture
def test_client():
    return TestClient(app)



