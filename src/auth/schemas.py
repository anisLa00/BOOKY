from pydantic import BaseModel ,Field
from src.books.schemas import Book
from src.review.schemas import ReviewModel
from typing import List
import uuid
from datetime import datetime




class UserCreateModel(BaseModel):
    first_name:str= Field(max_length=20)
    last_name:str= Field(max_length=20)
    username:str =Field(max_length=20)
    Email:str =Field(max_length=50)
    password:str = Field(min_length=6)



class UserModel(BaseModel):
        uid:uuid.UUID
        username:str
        Email:str
        first_name:str
        last_name:str
        password_hash:str = Field(exclude=True)
        is_verified:bool 
        created_at:datetime 
        updated_at:datetime
        

class UserBookModel(UserModel):
        books:List[Book]
        reviews:List[ReviewModel]
       
        

class UserLoginUser(BaseModel):
      Email:str =Field(max_length=50)
      password:str = Field(min_length=6)

class EmailsModel(BaseModel):
       adresses:List[str]      


class ResetRequestPasswordModel(BaseModel):
       email:str

class ResetPasswordConfirmModel(BaseModel):
       new_password:str
       confirm_new_password:str       
