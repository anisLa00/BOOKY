from fastapi import APIRouter , status , Depends,BackgroundTasks

from src.db.main  import get_session
import uuid
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.schemas import UserCreateModel , UserModel ,UserLoginUser,UserBookModel,EmailsModel,ResetPasswordConfirmModel,ResetRequestPasswordModel
from .service import UserService
from .utils import verify_password, create_acces_token,create_url_safe_token,decode_url_safe_token,generate_passwd_hash
from datetime import timedelta ,datetime,timezone
from fastapi.responses import JSONResponse
from .dependencies import RefreshTokenBearer,AccessTokenBearer,get_current_user
from src.celery import send_email
from src.db.redis import add_jti_to_blocklist
from .dependencies import RoleChecker
from src.errors import  UserAlreadyExists,InvalidToken,InvalidCredentials,UserNotFound
from src.config import Config
from src.db.main import get_session
from fastapi.exceptions import HTTPException





auth_router = APIRouter()
user_service = UserService()
role_checker =RoleChecker(["admin","user"])

REFRESH_TOKEN_EXPIRY=2


@auth_router.post("/Send_mail")
async def send_mail(emails:EmailsModel):
    emails=emails.adresses

    html="<h1>welcome to the app</h1>"
    subject="Eerify your Email"

    send_email.delay(emails,subject,html)

    return {"message":"email sent successfully "}



@auth_router.post("/Singup",
        
        status_code=status.HTTP_201_CREATED)

async def create_user_Account(
        User_data:UserCreateModel ,
        bg_tasks:BackgroundTasks, 
        session:AsyncSession=Depends(get_session)):
    
    email= User_data.Email

    user_exist=await user_service.exist_user(email , session)

    if user_exist:
        raise UserAlreadyExists()

    new_user= await  user_service.Create_user(User_data,session)
    new_user.verification_email_sent_at=datetime.now()
    await session.commit()
    token=create_url_safe_token({"email":email})

    link =f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"

    html=f"""<b1>Verify your Email</b1>
    <p> click to this <a href="{link}"> link </a>link to verify </p>
     """
    emails=[email]
    subject="Eerify your Email"

    send_email.delay(emails,subject,html)
    

    return {
        "meassage":"the account created ! , check your email",
        "user":new_user
        }

@auth_router.get("/verify/{token}")
async def verify_user_account(token:str, session:AsyncSession=Depends(get_session)):

    token_data=decode_url_safe_token(token)

    if token_data is None :
        return JSONResponse(
            status_code=400,
            content={"message":"invalid token"}
        )

    user_email = token_data.get("email")
    if user_email:
        user= await user_service.get_user_by_email(user_email,session)

        if not user:
            raise UserNotFound()

        await user_service.user_update(user,{"is_verified":True},session)

        return JSONResponse(
            content={
                "message":"Account verified successfully"
            },
            status_code=status.HTTP_200_OK
        )
    return JSONResponse(content={
                    "message":"Account accured during verification"
                },
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )


@auth_router.post("/resend-verification")
async def resend_verification(
    email: str,
    session: AsyncSession = Depends(get_session)
):
    user = await user_service.get_user_by_email(email, session)

    if not user:
        raise UserNotFound()

    if user.is_verified:
        return {"message": "Account is already verified"}

    if user.verification_email_sent_at:
        elapsed = datetime.now() - user.verification_email_sent_at

        if elapsed < timedelta(minutes=1):
            return {"message": "Please wait 1 minutes before requesting another email"}
    

    token = create_url_safe_token({"email": user.Email})

    link =f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"
    
    html=f"""<b1>Verify your Email</b1>
        <p> click to this <a href="{link}> link </a>link to verify </p>
         """
    subject="Verify your Email"
    emails=[email]     
    send_email.delay(emails,subject,html)


    user.verification_email_sent_at = datetime.now()
    user.verification_email_sent_at = datetime.now()
    await session.commit()
    
    return {
            "meassage":"the account created ! , check your email",
            
            }



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
    raise InvalidCredentials()
    

@auth_router.get("/refresh_token")  
async def get_new_access_token(token_details:dict=Depends(RefreshTokenBearer())) :
    expiry_timestamp=token_details["exp"]

    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_acces_token(
            user_data=token_details["user"]
        )

        return JSONResponse(content={"access_token":new_access_token})

    raise InvalidToken()
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


@auth_router.post("/reset-your-passaword")
async def reset_password(email_data:ResetRequestPasswordModel):
    email= email_data.email
    token=create_url_safe_token({"email":email})
    
    link =f"http://{Config.DOMAIN}/api/v1/auth/password-reset-confirm/{token}"
    
    html_message=f"""<b1>Reset your passaword</b1>
    <p> click to this <a href="{link}"> link </a>Reset your Password </p>
         """
    subject="Verify your Email"

    emails=[email]  

    send_email.delay(emails,subject,html_message)
    
    return JSONResponse(
        content={
            "meassage":"please check your Email to instrucitons to rest password",
        },
        status_code=status.HTTP_200_OK,
    )


@auth_router.post("/password-reset-confirm/{token}")
async def rest_password_account(token:str,passwords:ResetPasswordConfirmModel, session:AsyncSession=Depends(get_session)):

    new_password=passwords.new_password
    confrim_password= passwords.confirm_new_password


    if new_password != confrim_password:
        raise HTTPException(detail="passwords is not match",status_code=status.HTTP_400_BAD_REQUEST)
    

    token_data=decode_url_safe_token(token)
    

    user_email = token_data.get("email")
    if user_email:
        user= await user_service.get_user_by_email(user_email,session)

        if not user:
            raise UserNotFound()

        password_hash= generate_passwd_hash(new_password)

        await user_service.user_update(user,{"password_hash":password_hash},session)

        return JSONResponse(
            content={
                "message":"password has been updated"
            },
            status_code=status.HTTP_200_OK
        )
    return JSONResponse(content={
                    "message":"Account accured during password reset"
                },
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )



    







    

    

