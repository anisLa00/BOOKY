"""Load test-only settings before importing the application package."""
import os

os.environ.update(
    DATABASE_URL="postgresql+asyncpg://booky_test:booky_test@localhost/booky_test",
    JWT_SECERT="booky-tests-only-not-a-production-secret",
    JWT_ALGORITHM="HS256",
    REDIS_URL="redis://localhost:6379/15",
    MAIL_USERNAME="booky-tests",
    MAIL_PASSWORD="test-only-password",
    MAIL_FROM="tests@example.com",
    MAIL_PORT="587",
    MAIL_SERVER="localhost",
    MAIL_FROM_NAME="Booky Tests",
    DOMAIN="localhost:8000",
)
