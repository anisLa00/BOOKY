def test_get_all_books(
    test_client, authenticated_user, fake_book_service, fake_session
):
    fake_book_service.get_all_book.return_value = []
    response = test_client.get("/api/v1/books/")
    assert response.status_code == 200
    assert response.json() == []
    fake_book_service.get_all_book.assert_awaited_once_with(fake_session)
