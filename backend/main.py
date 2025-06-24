from fastapi import FastAPI
from passlib.context import CryptContext
from backend.auth_routes import auth_router
from backend.order_routes import order_router
# from backend.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


app = FastAPI()

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
