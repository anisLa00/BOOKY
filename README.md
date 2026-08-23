# BOOKY 📚

BOOKY is a backend REST API for managing books, users, reviews, and tags.

The project is built with Python and FastAPI and uses PostgreSQL as the main database.

## 🚀 Features

- 🔐 User authentication
- 👤 User management
- 📚 Book management
- ⭐ Reviews and ratings
- 🏷️ Book tags
- 📧 Email verification
- ⚡ Background tasks with Celery
- 🔴 Redis for task queuing
- 🗄️ PostgreSQL database
- 🔄 Database migrations with Alembic
- 🧪 API testing with Pytest
- 📖 Interactive API documentation with Swagger

## 🛠️ Tech Stack

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- Redis
- Celery
- Pytest
- Pydantic

## 📁 Project Structure

```text
BOOKY/
├── migrations/
├── src/
│   ├── auth/
│   ├── books/
│   ├── review/
│   ├── tags/
│   ├── db/
│   ├── tests/
│   ├── celery.py
│   ├── config.py
│   ├── mail.py
│   ├── middleware.py
│   └── main.py
├── .gitignore
├── alembic.ini
├── requirements.txt
└── README.md