# BOOKY 📚

A backend REST API for managing books, users, reviews, and tags.

BOOKY is built with **Python + FastAPI** and uses **PostgreSQL** as its main database. The project also includes authentication, email verification, Redis/Celery background processing, database migrations, and automated API tests.

## ✨ Features

- 🔐 User authentication and JWT authorization
- 👤 User management
- 📚 Book management
- ⭐ Reviews and ratings
- 🏷️ Book tags
- 📧 Email verification
- ⚡ Background tasks with Celery
- 🔴 Redis for task processing
- 🗄️ PostgreSQL database
- 🔄 Database migrations with Alembic
- 🧪 API testing with Pytest
- 📖 Interactive API documentation with Swagger/OpenAPI

## 🛠️ Tech Stack

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- Alembic
- Redis
- Celery
- Pytest
- JWT
- SMTP / Email
- Swagger / OpenAPI

## 🏗️ Project Structure

```text
BOOKY/
├── migrations/
│   └── versions/
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
├── LICENSE
└── README.md