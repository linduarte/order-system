from fastapi import APIRouter, Depends, HTTPException
from backend.models import Usuario
from backend.dependencies import pegar_sessao, verificar_token
from backend.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from backend.schemas import UsuarioSchema, LoginSchema
from sqlalchemy.orm import Session
from jose import  jwt ,JWTError
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm
# Importe a função do seu novo arquivo utils.py
from backend.utils import save_token_to_file
import logging

# Criação do contexto bcrypt para hashing e verificação de senhas
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


auth_router = APIRouter(prefix="/auth", tags=["auth"])


def criar_token(id_usuario, duracao_token=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    """
    Gera um token JWT com informações do usuário e tempo de expiração.

    :param id_usuario: O ID do usuário para incluir no payload do token.
    :param duracao_token: A duração do token (padrão 30 minutos).
    :return: O token JWT codificado.
    """
    try:
        data_expiracao = datetime.now(timezone.utc) + duracao_token
        dic_info = {
            "sub": str(id_usuario),  # O 'sub' é usado para identificar o usuário
            "exp": data_expiracao,  # Definir a data de expiração do token
        }
        jwt_codificado = jwt.encode(dic_info, SECRET_KEY, algorithm=ALGORITHM)  # Codifica o token com a chave secreta
        return jwt_codificado
    except JWTError as e:
        logging.error(f"Erro ao criar o token JWT: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao criar o token")
    except Exception as e:
        logging.error(f"Erro inesperado ao criar o token JWT: {e}")
        raise HTTPException(status_code=500, detail="Erro interno inesperado")





def autenticar_usuario(email, senha, session):
    """
    Autentica o usuário verificando o email e a senha.
    
    :param email: O email do usuário.
    :param senha: A senha do usuário.
    :param session: A sessão do banco de dados para consulta.
    :return: O usuário autenticado ou False se falhar.
    """
    try:
        # Busca o usuário no banco de dados
        usuario = session.query(Usuario).filter(Usuario.email == email).first()
        
        # Se o usuário não for encontrado, retorna erro
        if not usuario:
            logging.warning(f"Tentativa de login com email não encontrado: {email}")
            raise HTTPException(status_code=400, detail="Usuário não encontrado ou credenciais inválidas")
        
        # Verifica a senha
        if not bcrypt_context.verify(senha, usuario.senha):
            logging.warning(f"Tentativa de login falhada com senha incorreta para o email: {email}")
            raise HTTPException(status_code=400, detail="Usuário não encontrado ou credenciais inválidas")
        
        # Se tudo der certo, retorna o usuário
        return usuario
    
    except Exception as e:
        logging.error(f"Erro ao tentar autenticar usuário {email}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao realizar a autenticação")



@auth_router.get("/")
async def home():
    """
    Essa é a rota padrão de autenticação do nosso sistema
    """
    return {
        "mensagem": "Você acessou a rota padrão de autenticação",
        "autenticado": False,
    }


@auth_router.post("/criar_conta")
async def criar_conta(
    usuario_schema: UsuarioSchema, session: Session = Depends(pegar_sessao)
):
    usuario = (
        session.query(Usuario).filter(Usuario.email == usuario_schema.email).first()
    )
    if usuario:
        # ja existe um usuario com esse email
        raise HTTPException(status_code=400, detail="E-mail do usuário já cadastrado")
    else:
        senha_criptografada = bcrypt_context.hash(usuario_schema.senha)
        novo_usuario = Usuario(
            usuario_schema.nome,
            usuario_schema.email,
            senha_criptografada,
            usuario_schema.ativo,
            usuario_schema.admin,
        )
        session.add(novo_usuario)
        session.commit()
        return {"mensagem": f"usuário cadastrado com sucesso {usuario_schema.email}"}


# login -> email e senha -> token JWT (Json Web Token) ahuyba786dabd86a5vdba865dvad786and
@auth_router.post("/login")
async def login(login_schema: LoginSchema, session: Session = Depends(pegar_sessao)):
    try:
        usuario = autenticar_usuario(login_schema.email, login_schema.senha, session)
        if not usuario:
            raise HTTPException(
                status_code=400, detail="Usuário não encontrado ou credenciais inválidas"
            )

        access_token = criar_token(usuario.id)
        refresh_token = criar_token(usuario.id, duracao_token=timedelta(days=7))

        # --- AQUI ESTÁ A MUDANÇA ---
        # Chame a função para salvar o access_token no arquivo.
        save_token_to_file(access_token)
        # --- FIM DA MUDANÇA ---

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
        }
    except Exception as e:
        logging.error(f"Erro no login: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao realizar login")



@auth_router.post("/login-form")
async def login_form(
    dados_formulario: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(pegar_sessao),
):
    usuario = autenticar_usuario(
        dados_formulario.username, dados_formulario.password, session
    )
    if not usuario:
        raise HTTPException(
            status_code=400, detail="Usuário não encontrado ou credenciais inválidas"
        )
    else:
        access_token = criar_token(usuario.id)
        return {"access_token": access_token, "token_type": "Bearer"}


@auth_router.get("/refresh")
async def use_refresh_token(usuario: Usuario = Depends(verificar_token)):
    access_token = criar_token(usuario.id)
    return {"access_token": access_token, "token_type": "Bearer"}
