"""SQLAlchemy models for the FastAPI application.

This module defines the database schema using SQLAlchemy ORM, including tables for users, orders, and order items.
It also includes methods for interacting with these models, such as calculating order prices.
"""

from sqlalchemy import (
    Boolean,
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship

# Database connection engine
db = create_engine("sqlite:///d:/reposground/work/order-system/backend/banco.db")
"""SQLAlchemy engine for connecting to the SQLite database."""

# Base class for declarative models
Base = declarative_base()
"""Declarative base class for SQLAlchemy models."""


class Usuario(Base):
    """Represents a user in the system.

    Attributes:
        id (int): Primary key, auto-incrementing user ID.
        nome (str): Name of the user.
        email (str): Email of the user, must be unique.
        senha (str): Hashed password of the user.
        ativo (bool): Indicates if the user account is active.
        admin (bool): Indicates if the user has administrative privileges.
    """

    __tablename__ = "usuarios"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String)
    email = Column("email", String, nullable=False)
    senha = Column("senha", String)
    ativo = Column("ativo", Boolean)
    admin = Column("admin", Boolean, default=False)

    def __init__(self, nome, email, senha, ativo=True, admin=False):
        """Initializes a new Usuario instance.

        Args:
            nome (str): The name of the user.
            email (str): The email of the user.
            senha (str): The hashed password of the user.
            ativo (bool, optional): Whether the user is active. Defaults to True.
            admin (bool, optional): Whether the user has admin privileges. Defaults to False.
        """
        self.nome = nome
        self.email = email
        self.senha = senha
        self.ativo = ativo
        self.admin = admin


class Pedido(Base):
    """Represents an order in the system.

    Attributes:
        id (int): Primary key, auto-incrementing order ID.
        status (str): Current status of the order (e.g., "PENDENTE", "CANCELADO", "FINALIZADO").
        usuario (int): Foreign key referencing the ID of the user who placed the order.
        preco (float): Total price of the order.
        itens (relationship): Relationship to the ItemPedido model, representing items in this order.
    """

    __tablename__ = "pedidos"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    status = Column("status", String)
    usuario = Column("usuario", ForeignKey("usuarios.id"))
    preco = Column("preco", Float)
    itens = relationship("ItemPedido", cascade="all, delete")

    def __init__(self, usuario, status="PENDENTE", preco=0):
        """Initializes a new Pedido instance.

        Args:
            usuario (int): The ID of the user placing the order.
            status (str, optional): The initial status of the order. Defaults to "PENDENTE".
            preco (float, optional): The initial price of the order. Defaults to 0.
        """
        self.usuario = usuario
        self.preco = preco
        self.status = status

    def calcular_preco(self):
        """Calculates and updates the total price of the order based on its items.

        The `preco` attribute is updated by summing the quantities multiplied by the unit prices of all associated `ItemPedido` instances.
        """
        self.preco = sum(item.quantidade * item.preco_unitario for item in self.itens)


class ItemPedido(Base):
    """Represents an item within an order.

    Attributes:
        id (int): Primary key, auto-incrementing item ID.
        quantidade (int): Quantity of the item.
        sabor (str): Flavor of the item.
        tamanho (str): Size of the item.
        preco_unitario (float): Unit price of the item.
        pedido (int): Foreign key referencing the ID of the order this item belongs to.
    """

    __tablename__ = "itens_pedido"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    quantidade = Column("quantidade", Integer)
    sabor = Column("sabor", String)
    tamanho = Column("tamanho", String)
    preco_unitario = Column("preco_unitario", Float)
    pedido = Column("pedido", ForeignKey("pedidos.id"))

    def __init__(self, quantidade, sabor, tamanho, preco_unitario, pedido):
        """Initializes a new ItemPedido instance.

        Args:
            quantidade (int): The quantity of the item.
            sabor (str): The flavor of the item.
            tamanho (str): The size of the item.
            preco_unitario (float): The unit price of the item.
            pedido (int): The ID of the order this item belongs to.
        """
        self.quantidade = quantidade
        self.sabor = sabor
        self.tamanho = tamanho
        self.preco_unitario = preco_unitario
        self.pedido = pedido
