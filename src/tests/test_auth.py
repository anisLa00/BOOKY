from src.auth import router as auth_routes
from src.auth.schemas import UserCreateModel


def test_user_creation(test_client, fake_session, fake_users):
    signup_data = {
        "first_name": "Test",
        "last_name": "Reader",
        "username": "reader",
        "Email": "reader@example.com",
        "password": "test-password",
    }
    # Preserve the existing public signup spelling in this repair.
    response = test_client.post("/api/v1/auth/Singup", json=signup_data)

    assert response.status_code == 201
    fake_users.exist_user.assert_awaited_once_with(signup_data["Email"], fake_session)
    fake_users.Create_user.assert_awaited_once_with(
        UserCreateModel(**signup_data), fake_session
    )
    fake_session.commit.assert_awaited_once()
    auth_routes.send_email.delay.assert_called_once()
