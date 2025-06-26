import os
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer


# Explicitly load the .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 120))
DATABASE_URL = os.getenv("DATABASE_URL")

oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login-form")
