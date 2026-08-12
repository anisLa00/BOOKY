from fastapi import APIRouter , status , Depends
from fastapi.exceptions import HTTPException
from src.db.main  import get_session
import uuid
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import DataError
from typing import List
from src.auth.schemas import UserCreateModel , UserModel ,UserLoginUser,UserBookModel
from .service import UserService
from .utils import verify_password, create_acces_token
from datetime import timedelta ,datetime
from fastapi.responses import JSONResponse
from .dependencies import RefreshTokenBearer,AccessTokenBearer,get_current_user
from src.db.redis import add_jti_to_blocklist
from .dependencies import RoleChecker





auth_router = APIRouter()
user_service = UserService()
role_checker =RoleChecker(["admin","user"])

REFRESH_TOKEN_EXPIRY=2


@auth_router.post("/Singup",
        response_model=UserModel,
        status_code=status.HTTP_201_CREATED)

async def create_user_Account(
        User_data:UserCreateModel , 
        session:AsyncSession=Depends(get_session)):
    
    email= User_data.Email

    user_exist=await user_service.exist_user(email , session)

    if user_exist:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="user with email already exist")

    return await  user_service.Create_user(User_data,session)

@auth_router.post("/login")
async def login_users(user_login_data:UserLoginUser , 
          session:AsyncSession=Depends(get_session)):
    email= user_login_data.Email
    password= user_login_data.password

    user= await user_service.get_user_by_email(email ,session)

    if user is not None :
        password_valid =verify_password(password, user.password_hash)
        if password_valid:
            acces_token = create_acces_token(
                user_data={
                         "email":user.Email,
                         "user_uid":str(user.uid),
                         "role":user.role 
            }
            )

            refresh_token=create_acces_token(
                user_data={
                    "email":user.Email,
                    "user_uid":str(user.uid)
                          },
                refresh=True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY)
            )


            return JSONResponse(
                content={
                    "message":"login successfll",
                    "acces_token":acces_token,
                    "refresh_token":refresh_token,
                    "user":{
                        "email":user.Email,
                        "uid":str(user.uid)
                    }
                }
            )
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="invalid email or password"
    )

@auth_router.get("/refresh_token")  
async def get_new_access_token(token_details:dict=Depends(RefreshTokenBearer())) :
    expiry_timestamp=token_details["exp"]

    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_acces_token(
            user_data=token_details["user"]
        )

        return JSONResponse(content={"access_token":new_access_token})

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="invalid or expired token")

@auth_router.get("/logout")
async def revooke_token(token_details:dict=Depends(AccessTokenBearer())):
    jti=token_details["jti"]

    await add_jti_to_blocklist(jti)



    return JSONResponse(content={
        "meesage":"Logged our successfully"},
        status_code=status.HTTP_200_OK
    )
@auth_router.get("/me", response_model=UserBookModel)
async def get_current_user(user:dict=Depends(get_current_user),__:bool=Depends(role_checker)):
    return user 

    







    

    

