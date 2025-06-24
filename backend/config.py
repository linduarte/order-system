import os
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer


load_dotenv(
    dotenv_path="d:/reposground/work/order-system/backend/.env"
)  # Explicit path to .env

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))


oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login-form")
