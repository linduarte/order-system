"""This is the main FastAPI application file.

It initializes the FastAPI app, configures password hashing, and includes API routers for authentication and order management.
"""

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from backend.auth_routes import auth_router
from backend.order_routes import order_router

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")


app = FastAPI(
    title="My FastAPI Application",
    description="This is a sample FastAPI application with authentication and order management.",
    version="1.0.0",
)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
"""CryptContext for handling password hashing using the bcrypt scheme."""
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/-form"
)  # Placeholder for OAuth2 scheme, if needed later


app.include_router(auth_router)
app.include_router(order_router)

# para rodar o nosso código, executar no terminal: uvicorn main:app --reload

# endpoint:
# dominio.com/pedidos


# Rest APIs
# Get -> leitura/pegar
# Post -> enviar/criar
# Put/Patch -> edição
# Delete -> deletar
