"""Configuration settings for the FastAPI application.

This module loads environment variables and defines constants used throughout the application,
such as secret keys, algorithms, token expiration times, and database URLs.
"""

from pathlib import Path
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
import os


# Explicitly load the .env file using pathlib
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

SECRET_KEY = os.getenv("SECRET_KEY")
"""The secret key used for JWT encoding and decoding."""
ALGORITHM = os.getenv("ALGORITHM")
"""The algorithm used for JWT signing (e.g., 'HS256')."""
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 120))
"""The expiration time for access tokens in minutes."""
DATABASE_URL = os.getenv("DATABASE_URL")
"""The URL for connecting to the database."""

oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login-form")
"""OAuth2PasswordBearer instance for handling token-based authentication."""
