from datetime import date, datetime
from unittest.mock import Mock
from uuid import uuid4

import pytest
from sqlalchemy.exc import SQLAlchemyError

from src.db.models import Book


@pytest.fixture
def stored_book(fake_session, authenticated_user):
    book = Book(
        uid=uuid4(), title="Original title", author="Original author",
        publisher="Original publisher", published_date=date(2024, 1, 1),
        page_count=120, language="English", user_uid=authenticated_user.uid,
        created_at=datetime(2024, 1, 1), updated_at=datetime(2024, 1, 1),
    )
    result = Mock()
    result.first.return_value = book
    fake_session.exec.return_value = result
    return book


def test_patch_one_field_preserves_omitted_values(test_client, stored_book, fake_session):
    response = test_client.patch(
        f"/api/v1/books/{stored_book.uid}", json={"title": "Updated title"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated title"
    assert data["author"] == "Original author"
    assert data["publisher"] == "Original publisher"
    assert data["page_count"] == 120
    assert data["language"] == "English"
    assert data["published_date"] == "2024-01-01"
    assert stored_book.updated_at > datetime(2024, 1, 1)
    fake_session.commit.assert_awaited_once()
    fake_session.refresh.assert_awaited_once_with(stored_book)


def test_patch_multiple_fields_commits_once(test_client, stored_book, fake_session):
    response = test_client.patch(
        f"/api/v1/books/{stored_book.uid}",
        json={"title": "Updated title", "author": "Updated author",
              "publisher": "Updated publisher", "page_count": 200, "language": "French"},
    )
    assert response.status_code == 200
    assert response.json()["page_count"] == 200
    assert response.json()["language"] == "French"
    fake_session.commit.assert_awaited_once()


def test_empty_patch_does_not_write(test_client, stored_book, fake_session):
    response = test_client.patch(f"/api/v1/books/{stored_book.uid}", json={})
    assert response.status_code == 200
    assert response.json()["title"] == "Original title"
    assert stored_book.updated_at == datetime(2024, 1, 1)
    fake_session.commit.assert_not_awaited()
    fake_session.refresh.assert_not_awaited()


@pytest.mark.parametrize("field", ["title", "author", "publisher", "page_count", "language"])
def test_patch_rejects_null(test_client, stored_book, fake_session, field):
    response = test_client.patch(f"/api/v1/books/{stored_book.uid}", json={field: None})
    assert response.status_code == 422
    fake_session.exec.assert_not_awaited()
    fake_session.commit.assert_not_awaited()


def test_patch_invalid_uuid_is_validation_error(test_client, authenticated_user, fake_session):
    response = test_client.patch(
        "/api/v1/books/not-a-uuid",
        json={"title": "New", "author": "Author", "publisher": "Publisher",
              "page_count": 100, "language": "English"},
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["path", "book_uid"]
    fake_session.exec.assert_not_awaited()


def test_patch_missing_book_returns_not_found(test_client, stored_book, fake_session):
    fake_session.exec.return_value.first.return_value = None
    response = test_client.patch(f"/api/v1/books/{uuid4()}", json={"title": "New"})
    assert response.status_code == 404
    assert response.json()["error_code"] == "book_not_found"
    fake_session.commit.assert_not_awaited()


def test_patch_database_failure_rolls_back(test_client, stored_book, fake_session):
    fake_session.commit.side_effect = SQLAlchemyError("Test database failure")
    response = test_client.patch(f"/api/v1/books/{stored_book.uid}", json={"title": "New"})
    assert response.status_code == 500
    assert response.json()["error_code"] == "server_error"
    fake_session.rollback.assert_awaited_once()
    fake_session.refresh.assert_not_awaited()


def test_patch_requires_authentication(test_client, fake_session):
    response = test_client.patch(f"/api/v1/books/{uuid4()}", json={"title": "New"})
    assert response.status_code in (401, 403)
    fake_session.exec.assert_not_awaited()


def test_openapi_mounts_all_routers_under_v1(test_client):
    response = test_client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    paths = response.json()["paths"]
    for prefix in ("/api/v1/books", "/api/v1/auth", "/api/v1/reviews", "/api/v1/tag"):
        assert any(path.startswith(prefix) for path in paths)
    assert not any("{version}" in path for path in paths)
