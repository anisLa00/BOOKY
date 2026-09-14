from pydantic import BaseModel, field_validator
from datetime import datetime , date
from src.review.schemas import ReviewModel
from typing import List
import uuid
from src.tags.schemas import TagModel

class Book(BaseModel):
    uid: uuid.UUID
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    created_at: datetime
    updated_at: datetime 
    

class BookDetails(Book):
    tags:List[TagModel]
    reviews:List[ReviewModel]    

class BookCreateModel(BaseModel):
        title: str
        author: str
        publisher: str
        published_date: date
        page_count: int
        language: str
    

class BookUpdateModel(BaseModel):
    title: str | None = None
    author: str | None = None
    publisher: str | None = None
    page_count: int | None = None
    language: str | None = None

    @field_validator("title", "author", "publisher", "page_count", "language")
    @classmethod
    def reject_null(cls, value):
        # Fields may be omitted, but their database columns cannot store NULL.
        if value is None:
            raise ValueError("Omit the field instead of setting it to null")
        return value
