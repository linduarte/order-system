"""Authentication routes for the FastAPI application.

This module defines API endpoints related to user authentication, including account creation, login, and token refreshing.
It uses JWT for token management and bcrypt for password hashing.
"""

import logging
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from backend.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from backend.dependencies import pegar_sessao
from backend.models import Usuario
from backend.schemas import LoginSchema, UsuarioSchema

# Importe a função do seu novo arquivo utils.py
from backend.utils import save_token_to_file

# Criação do contexto bcrypt para hashing e verificação de senhas
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


auth_router = APIRouter(prefix="/auth", tags=["auth"])


def criar_token(
    id_usuario, duracao_token=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
):
    """
    Gera um token JWT com informações do usuário e tempo de expiração.

    :param id_usuario: O ID do usuário para incluir no payload do token.
    :param duracao_token: A duração do token (padrão 30 minutos).
    :return: O token JWT codificado.
    """
    try:
        data_expiracao = datetime.now(UTC) + duracao_token
        dic_info = {
            "sub": str(id_usuario),  # O \'sub\' é usado para identificar o usuário
            "exp": data_expiracao,  # Definir a data de expiração do token
        }
        jwt_codificado = jwt.encode(
            dic_info, SECRET_KEY, algorithm=ALGORITHM
        )  # Codifica o token com a chave secreta
        return jwt_codificado
    except JWTError as e:
        logging.error(f"Erro ao criar o token JWT: {e}")
        raise HTTPException(
            status_code=500, detail="Erro interno ao criar o token"
        ) from e
    except Exception as e:
        logging.error(f"Erro inesperado ao criar o token JWT: {e}")
        raise HTTPException(status_code=500, detail="Erro interno inesperado") from e


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
            raise HTTPException(
                status_code=400,
                detail="Usuário não encontrado ou credenciais inválidas",
            )

        # Verifica a senha
        if not bcrypt_context.verify(senha, usuario.senha):
            logging.warning(
                f"Tentativa de login falhada com senha incorreta para o email: {email}"
            )
            raise HTTPException(
                status_code=400,
                detail="Usuário não encontrado ou credenciais inválidas",
            )

        # Se tudo der certo, retorna o usuário
        return usuario

    except Exception as e:
        logging.error(f"Erro ao tentar autenticar usuário {email}: {e}")
        raise HTTPException(
            status_code=500, detail="Erro ao realizar a autenticação"
        ) from e


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
    """Cria uma nova conta de usuário.

    Args:
        usuario_schema (UsuarioSchema): Os dados do novo usuário a ser criado.
        session (Session, optional): A sessão do banco de dados. Injetada por dependência.

    Raises:
        HTTPException: Se o e-mail do usuário já estiver cadastrado.

    Returns:
        dict: Uma mensagem de sucesso após o cadastro do usuário.
    """
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
    """Realiza o login do usuário e retorna tokens de acesso e refresh.

    Args:
        login_schema (LoginSchema): Os dados de login do usuário (email e senha).
        session (Session, optional): A sessão do banco de dados. Injetada por dependência.

    Raises:
        HTTPException: Se o usuário não for encontrado ou as credenciais forem inválidas.
        HTTPException: Em caso de erro interno ao realizar o login.

    Returns:
        dict: Um dicionário contendo o access_token, refresh_token e o tipo de token.
    """
    try:
        usuario = autenticar_usuario(login_schema.email, login_schema.senha, session)
        if not usuario:
            raise HTTPException(
                status_code=400,
                detail="Usuário não encontrado ou credenciais inválidas",
            )

        access_token = criar_token(usuario.id)
        refresh_token = criar_token(usuario.id, duracao_token=timedelta(days=7))

        # Chame a função para salvar o access_token no arquivo.
        save_token_to_file(access_token)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
        }
    except Exception as e:
        logging.error(f"Erro no login: {e}")
        raise HTTPException(
            status_code=500, detail="Erro interno ao realizar login"
        ) from e


@auth_router.post("/login-form")
async def login_form(
    dados_formulario: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(pegar_sessao),
):
    """Realiza o login do usuário através de um formulário OAuth2.

    Args:
        dados_formulario (OAuth2PasswordRequestForm, optional): Dados do formulário de login.
        session (Session, optional): A sessão do banco de dados. Injetada por dependência.

    Raises:
        HTTPException: Se o usuário não for encontrado ou as credenciais forem inválidas.

    Returns:
        dict: Um dicionário contendo o access_token e o tipo de token.
    """
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


@auth_router.post("/refresh")
async def refresh_access_token(
    refresh_token: str, session: Session = Depends(pegar_sessao)
):
    """Atualiza o token de acesso usando um token de refresh válido.

    Args:
        refresh_token (str): O refresh token válido fornecido pelo cliente.
        session (Session): A sessão do banco de dados. Injetada por dependência.

    Raises:
        HTTPException: Se o refresh token for inválido, expirado ou o usuário não for encontrado.

    Returns:
        dict: Um dicionário contendo o novo access_token e o tipo de token.
    """
    try:
        # Decodificar o refresh token
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))

        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")

        # Verificar se o usuário ainda existe no banco de dados
        usuario = session.query(Usuario).filter(Usuario.id == user_id).first()
        if not usuario:
            logging.warning(f"Tentativa de refresh com usuário inexistente: {user_id}")
            raise HTTPException(status_code=401, detail="Usuário não encontrado")

        # Verificar se o usuário ainda está ativo
        if not usuario.ativo:
            logging.warning(f"Tentativa de refresh com usuário inativo: {user_id}")
            raise HTTPException(status_code=401, detail="Usuário inativo")

        # Criar novo access token
        new_access_token = criar_token(usuario.id)

        # Salvar o novo access token (mantendo o mesmo refresh token)
        save_token_to_file(new_access_token, refresh_token)

        logging.info(f"Access token renovado com sucesso para usuário: {user_id}")

        return {"access_token": new_access_token, "token_type": "Bearer"}

    except JWTError as e:
        logging.warning(f"Refresh token inválido ou expirado: {e}")
        raise HTTPException(
            status_code=401, detail="Refresh token inválido ou expirado"
        ) from e
    except Exception as e:
        logging.error(f"Erro ao renovar access token: {e}")
        raise HTTPException(
            status_code=500, detail="Erro interno ao renovar token"
        ) from e
