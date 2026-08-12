from fastapi import APIRouter, status,Depends
from src.books.schemas import BookUpdateModel, Book, BookCreateModel,BookDetails
from fastapi.exceptions import HTTPException
from src.db.main import get_session
from src.books.service import BookService
from sqlmodel.ext.asyncio.session import AsyncSession
import uuid
from sqlalchemy.exc import DataError
from src.auth.dependencies import AccessTokenBearer,RoleChecker
from typing import List

book_router = APIRouter()
book_service = BookService()
access_token_bearer=AccessTokenBearer()
role_checker =Depends(RoleChecker(["admin","user"]))
@book_router.get("/", response_model=List[Book],dependencies=[role_checker])
async def get_all_books(session:AsyncSession=Depends(get_session),token_details:dict=Depends(access_token_bearer)):
    
    books = await book_service.get_all_book(session)
    return books

@book_router.get("/user/{user_uid}", response_model=List[BookDetails],dependencies=[role_checker])

async def get_user_book_submissions(
    user_uid:str,
    session:AsyncSession=Depends(get_session),
    token_details:dict=Depends(access_token_bearer)):
    
    books = await book_service.get_user_books(user_uid,session)
    return books


@book_router.post("/", status_code=status.HTTP_201_CREATED, response_model=Book,dependencies=[role_checker],)
async def create_a_book(book_data: BookCreateModel, session:AsyncSession=Depends(get_session),
                        token_details:dict=Depends(access_token_bearer),) -> dict:
    user_uid = token_details.get("user")["user_uid"]
    new_book = await book_service.Create_book(book_data,session,user_uid)

    return new_book


@book_router.get("/{book_uid}" , response_model=BookDetails,dependencies=[role_checker])
async def get_book(book_uid: str,session:AsyncSession=Depends(get_session),token_details:dict=Depends(access_token_bearer)) -> dict:
    user_id= token_details.get("user")["user_uid"]
    book = await book_service.get_book(book_uid,session)

    if book:
        return book
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="book not found")


@book_router.patch("/{book_uid}", response_model=Book,dependencies=[role_checker])
async def update_book(book_uid: str, book_update_date: BookUpdateModel, session:AsyncSession=Depends(get_session)) -> dict:

    try:
        updated_book = await book_service.update_book(book_uid , book_update_date, session)

    except Exception :
        
        raise HTTPException(status_code=400, detail="INVALID book ID")

    if updated_book is None:

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="book not found")

    return updated_book


        


@book_router.delete("/{book_uid}",dependencies=[role_checker])
async def remove_book(book_uid: str,session:AsyncSession=Depends(get_session),token_details:dict=Depends(access_token_bearer)):
    book_to_detete = await book_service.delate_book(book_uid,session)

    if book_to_detete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="book not found")
    else:
        return {"message":"book deleted succsefully"}



@book_router.delete("/",dependencies=[role_checker])    
async def delete_all_books(
    session:AsyncSession = Depends(get_session),
    token_details:dict=Depends(access_token_bearer)
):
    delete_all = await book_service.delete_all_books(session)

    if delete_all is None:

        raise HTTPException(status_code=404, detail="no books found")
    else:
        return {"message":"All books deleted succsefully"}


    