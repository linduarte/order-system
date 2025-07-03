"""Pydantic schemas for data validation and serialization in the FastAPI application.

This module defines the data structures used for request and response bodies,
ensuring data integrity and providing clear documentation for API endpoints.
"""

from pydantic import BaseModel
from typing import Optional, List


class UsuarioSchema(BaseModel):
    """Schema for user creation and update operations.

    Attributes:
        nome (str): The name of the user.
        email (str): The email address of the user.
        senha (str): The password for the user account.
        ativo (Optional[bool]): Indicates if the user account is active. Defaults to True if not provided.
        admin (Optional[bool]): Indicates if the user has administrative privileges. Defaults to False if not provided.
    """

    nome: str
    email: str
    senha: str
    ativo: Optional[bool]
    admin: Optional[bool]

    class Config:
        from_attributes = True


class PedidoSchema(BaseModel):
    """Schema for creating a new order.

    Attributes:
        id_usuario (int): The ID of the user placing the order.
    """

    usuario: int

    class Config:
        from_attributes = True


class LoginSchema(BaseModel):
    """Schema for user login credentials.

    Attributes:
        email (str): The email address of the user.
        senha (str): The password for the user account.
    """

    email: str
    senha: str

    class Config:
        from_attributes = True


class ItemPedidoSchema(BaseModel):
    """Schema for an item within an order.

    Attributes:
        quantidade (int): The quantity of the item.
        sabor (str): The flavor of the item.
        tamanho (str): The size of the item.
        preco_unitario (float): The unit price of the item.
    """

    quantidade: int
    sabor: str
    tamanho: str
    preco_unitario: float

    class Config:
        from_attributes = True


class ResponsePedidoSchema(BaseModel):
    """Schema for representing an order in API responses.

    Attributes:
        id (int): The unique ID of the order.
        status (str): The current status of the order (e.g., "PENDENTE", "CANCELADO", "FINALIZADO").
        preco (float): The total price of the order.
        itens (List[ItemPedidoSchema]): A list of items included in the order.
    """

    id: int
    status: str
    preco: float
    itens: List[ItemPedidoSchema]

    class Config:
        from_attributes = True
