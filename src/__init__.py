from fastapi import FastAPI
from src.books.routes import book_router
from src.review.routes import review_router
from contextlib import asynccontextmanager
from src.auth.router import auth_router
from src.tags.routes import tag_router
from src.db.main import init_db


@asynccontextmanager
async def life_span(app:FastAPI):
    print(f"servere is start ......")
    from src.db.models import Book
    await init_db()
    yield
    print(f"server has been stoped......")


version = "v1"

app = FastAPI(
    title="Bookly",
    description="va rest api for a book rivew web service",
    version= version,
    
)


app.include_router(book_router , prefix="/api/{version}/books", tags=["books"])

app.include_router(auth_router , prefix="/api/{version}/auth", tags=["auth"])

app.include_router(review_router , prefix="/api/{version}/reviews", tags=["reviews"])

app.include_router(tag_router , prefix="/api/{version}/tag", tags=["tags"])


