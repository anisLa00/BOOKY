from src.auth.schemas import UserCreateModel

auth_prefix=f"api/v1/auth"
def test_ueser_creation(fake_session,fake_users,test_client):
    asignup_data={
    "first_name" :"ellafi",
    "last_name":"anis",
    "username":"anisansid",
    "Email":"anisellafi0@gmail.com",
    "password":"123467ds"
}
    
    response= test_client.post(
        url=f"{auth_prefix}/signup",
        json=asignup_data
    )

   
    user_data=UserCreateModel(**asignup_data)


    assert fake_users.user_exists_called_once()
    assert fake_users.user_exists_called_once_with(asignup_data["Email"],fake_session)
    assert fake_users.create_exists_called_once()
    assert fake_users.create_user_called_once_with(user_data,fake_session)
    
    

