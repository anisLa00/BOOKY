from fastapi import FastAPI , status
from pydantic import BaseModel
from typing import List
from fastapi.exceptions import HTTPException



app = FastAPI()

books = [
    {
        "id":1,
        "title": "think python",
        "author": "allen",
        "publisher":" relly media",
        "published_date":"2022-2-22",
        "page_count":1234,
        "language": "english",
    },
    {
            "id":2,
            "title": "think html",
            "author": "allen",
            "publisher":" relly media",
            "published_date":"2022-2-22",
            "page_count":1234,
            "language": "english",
        },
        {
                "id":3,
                "title": "think css",
                "author": "allen",
                "publisher":" relly media",
                "published_date":"2022-2-22",
                "page_count":1234,
                "language": "english",
            },
    {
            "id":4,
            "title": "think java",
            "author": "allen",
            "publisher":" relly media",
            "published_date":"2022-2-22",
            "page_count":1234,
            "language": "english",
        },
    {
            "id":5,
            "title": "think c++",
            "author": "allen",
            "publisher":" relly media",
            "published_date":"2022-2-22",
            "page_count":1234,
            "language": "english",
        },
    {
            "id":6,
            "title": "think angular",
            "author": "allen",
            "publisher":" relly media",
            "published_date":"2022-2-22",
            "page_count":1234,
            "language": "english",
        },
    {
            "id":7,
            "title": "think json",
            "author": "allen",
            "publisher":" relly media",
            "published_date":"2022-2-22",
            "page_count":1234,
            "language": "english",
        },                    
]

class Book(BaseModel):
        id:int
        title:str
        author:str
        publisher:str
        published_date:str
        page_count:int
        language:str
class BookUpdateModel(BaseModel):
             title:str
             author:str
             publisher:str
             page_count:int
             language:str

@app.get("/books", response_model=List[Book])
async def get_all_books():
    return books




@app.post("/books" , status_code=status.HTTP_201_CREATED)
async def create_a_book(book_data:Book) -> dict:
    new_book = book_data.model_dump()

    books.append(new_book)

    return new_book




@app.get("/books/{book_id}")
async def get_book(book_id:int) -> dict:
    for book in books:
         if book["id"] ==book_id:
              return book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="book not found")



@app.patch("/books/{book_id}")
async def update_book(book_id:int , book_update_date:BookUpdateModel) -> dict:
    for book in books:
          if book["id"] == book_id:
                book["title"] = book_update_date.title
                book["author"] = book_update_date.author
                book["publisher"] = book_update_date.publisher
                book["page_count"] = book_update_date.page_count
                book["language"] = book_update_date.language

                return book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="book not found")

@app.delete("/books/{book_id}" , status_code=status.HTTP_204_NO_CONTENT)
async def remove_book(book_id:int):
    for book in books:
        if book["id"] == book_id:
          books.remove(book)


          return {}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="book not found")    
    