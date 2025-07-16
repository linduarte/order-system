"""Module for common dependencies used in the FastAPI application.

This module provides functions for managing database sessions and verifying JWT tokens,
which are used as dependencies in various API routes.
"""

from fastapi import Depends, HTTPException
from jose import JWTError, jwt
from sqlalchemy.orm import Session, sessionmaker

from backend.config import ALGORITHM, SECRET_KEY, oauth2_schema
from backend.models import Usuario, db


def pegar_sessao():
    """Dependency that provides a SQLAlchemy database session.

    This function creates a new database session for each request and ensures it is closed after the request is completed.

    Yields:
        Session: A SQLAlchemy database session.
    """
    try:
        Session = sessionmaker(bind=db)
        session = Session()
        yield session
    finally:
        session.close()


def verificar_token(
    token: str = Depends(oauth2_schema), session: Session = Depends(pegar_sessao)
):
    """Dependency that verifies the authenticity and validity of a JWT token.

    This function decodes the provided JWT token, extracts the user ID, and retrieves the corresponding user from the database.

    Args:
        token (str): The JWT token provided in the request header (injected by OAuth2PasswordBearer).
        session (Session): The database session (injected by pegar_sessao).

    Raises:
        HTTPException: If the token is invalid, expired, or the user associated with the token is not found.

    Returns:
        Usuario: The authenticated user object.
    """
    try:
        dic_info = jwt.decode(token, SECRET_KEY, ALGORITHM)
        # pyrefly: ignore  # no-matching-overload
        id_usuario = int(dic_info.get("sub"))
    except JWTError as e:
        raise HTTPException(
        status_code=401, detail="Acesso Negado, verifique a validade do token"
    ) from e
    # verificar se o token é válido
    # extrair o ID do usuário do token
    usuario = session.query(Usuario).filter(Usuario.id == id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Acesso Inválido")
    return usuario
