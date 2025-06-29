"""Order management routes for the FastAPI application.

This module defines API endpoints related to order creation, cancellation, item management, and viewing.
It includes routes for both administrative and regular users, with appropriate authorization checks.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.dependencies import pegar_sessao, verificar_token
from backend.schemas import PedidoSchema, ItemPedidoSchema, ResponsePedidoSchema
from backend.models import Pedido, Usuario, ItemPedido
from typing import List


order_router = APIRouter(
    prefix="/pedidos", tags=["pedidos"], dependencies=[Depends(verificar_token)]
)


@order_router.get("/")
async def pedidos():
    """
    Essa é a rota padrão de pedidos do nosso sistema. Todas as rotas dos pedidos precisam de autenticação
    """
    return {"mensagem": "Você acessou a rota de pedidos"}


@order_router.post("/pedido")
async def criar_pedido(
    pedido_schema: PedidoSchema, session: Session = Depends(pegar_sessao)
):
    """Cria um novo pedido no sistema.

    Args:
        pedido_schema (PedidoSchema): O esquema do pedido contendo o ID do usuário.
        session (Session, optional): A sessão do banco de dados. Injetada por dependência.

    Returns:
        dict: Uma mensagem de sucesso com o ID do pedido criado.
    """
    novo_pedido = Pedido(usuario=pedido_schema.id_usuario)
    session.add(novo_pedido)
    session.commit()
    return {"mensagem": f"Pedido criado com sucesso. ID do pedido: {novo_pedido.id}"}


@order_router.post("/pedido/cancelar/{id_pedido}")
async def cancelar_pedido(
    id_pedido: int,
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token),
):
    """Cancela um pedido existente.

    Args:
        id_pedido (int): O ID do pedido a ser cancelado.
        session (Session, optional): A sessão do banco de dados. Injetada por dependência.
        usuario (Usuario, optional): O usuário autenticado. Injetado por dependência.

    Raises:
        HTTPException: Se o pedido não for encontrado.
        HTTPException: Se o usuário não tiver permissão para cancelar o pedido.

    Returns:
        dict: Uma mensagem de sucesso e os detalhes do pedido cancelado.
    """
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    if not usuario.admin and pedido.usuario != usuario.id:
        raise HTTPException(
            status_code=401, detail="Você não tem permissão para cancelar este pedido"
        )
    pedido.status = "CANCELADO"
    session.commit()
    return {
        "mensagem": f"Pedido número: {pedido.id} cancelado com sucesso",
        "pedido": pedido,
    }


@order_router.get("/pedidos/listar")
async def listar_todos_pedidos(
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token),
):
    """Lista todos os pedidos no sistema (apenas para administradores).

    Args:
        session (Session, optional): A sessão do banco de dados. Injetada por dependência.
        usuario (Usuario, optional): O usuário autenticado. Injetado por dependência.

    Raises:
        HTTPException: Se o usuário não for um administrador.

    Returns:
        dict: Uma lista de todos os pedidos.
    """
    if not usuario.admin:
        raise HTTPException(
            status_code=401, detail="Voce não tem autorização para fazer esta operação"
        )
    else:
        pedidos = session.query(Pedido).all()
        return {"pedidos": pedidos}


@order_router.post("/pedido/adicionar-item/{id_pedido}")
async def adicionar_item_pedido(
    id_pedido: int,
    item_pedido_schema: ItemPedidoSchema,
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token),
):
    """Adiciona um item a um pedido existente.

    Args:
        id_pedido (int): O ID do pedido ao qual o item será adicionado.
        item_pedido_schema (ItemPedidoSchema): O esquema do item do pedido a ser adicionado.
        session (Session, optional): A sessão do banco de dados. Injetada por dependência.
        usuario (Usuario, optional): O usuário autenticado. Injetado por dependência.

    Raises:
        HTTPException: Se o pedido não existir.
        HTTPException: Se o pedido já estiver finalizado ou cancelado.
        HTTPException: Se o usuário não tiver autorização para adicionar itens ao pedido.

    Returns:
        dict: Uma mensagem de sucesso, o ID do item adicionado e o preço atualizado do pedido.
    """
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não existente")
    if pedido.status in ["FINALIZADO", "CANCELADO"]:
        raise HTTPException(
            status_code=400,
            detail="Não é possível adicionar itens a pedidos FINALIZADO ou CANCELADO",
        )
    if not usuario.admin and pedido.usuario != usuario.id:
        raise HTTPException(
            status_code=401,
            detail="Você não tem autorização para realizar esta operação",
        )
    item_pedido = ItemPedido(
        item_pedido_schema.quantidade,
        item_pedido_schema.sabor,
        item_pedido_schema.tamanho,
        item_pedido_schema.preco_unitario,
        id_pedido,
    )
    session.add(item_pedido)
    pedido.calcular_preco()
    session.commit()
    return {
        "mensagem": "Item adicionado com sucesso ao pedido",
        "item_id": item_pedido.id,
        "preco_pedido": pedido.preco,
    }


@order_router.delete("/pedido/remover-item/{id_item_pedido}")
async def remover_item_pedido(
    id_item_pedido: int,
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token),
):
    """Remove um item de um pedido existente.

    Args:
        id_item_pedido (int): O ID do item do pedido a ser removido.
        session (Session, optional): A sessão do banco de dados. Injetada por dependência.
        usuario (Usuario, optional): O usuário autenticado. Injetado por dependência.

    Raises:
        HTTPException: Se o item do pedido não for encontrado.
        HTTPException: Se o pedido associado ao item não for encontrado.
        HTTPException: Se o pedido já estiver finalizado ou cancelado.
        HTTPException: Se o usuário não tiver autorização para remover o item.

    Returns:
        dict: Uma mensagem de sucesso, a quantidade de itens restantes no pedido e os detalhes do pedido atualizado.
    """
    # Fetch the item from the database
    item_pedido = (
        session.query(ItemPedido).filter(ItemPedido.id == id_item_pedido).first()
    )
    if not item_pedido:
        raise HTTPException(status_code=404, detail="Item do pedido não encontrado")

    # Fetch the associated order
    pedido = session.query(Pedido).filter(Pedido.id == item_pedido.pedido).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    # Validate the order status
    if pedido.status in ["FINALIZADO", "CANCELADO"]:
        raise HTTPException(
            status_code=400,
            detail="Não é possível remover itens de pedidos FINALIZADO ou CANCELADO",
        )

    # Validate user authorization
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(
            status_code=401,
            detail="Você não tem autorização para realizar esta operação",
        )

    # Remove the item and update the order price
    session.delete(item_pedido)
    pedido.calcular_preco()
    session.commit()

    return {
        "mensagem": "Item removido com sucesso",
        "quantidade_itens_pedido": len(pedido.itens),
        "pedido": pedido,
    }


# finalizar pedido
@order_router.post("/pedido/finalizar/{id_pedido}")
async def finalizar_pedido(
    id_pedido: int,
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token),
):
    """Finaliza um pedido, alterando seu status para 'FINALIZADO'.

    Args:
        id_pedido (int): O ID do pedido a ser finalizado.
        session (Session, optional): A sessão do banco de dados. Injetada por dependência.
        usuario (Usuario, optional): O usuário autenticado. Injetado por dependência.

    Raises:
        HTTPException: Se o pedido não for encontrado.
        HTTPException: Se o usuário não tiver autorização para finalizar o pedido.

    Returns:
        dict: Uma mensagem de sucesso e os detalhes do pedido finalizado.
    """
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    if not usuario.admin and pedido.usuario != usuario.id:
        raise HTTPException(
            status_code=401, detail="Você não autorização para fazer essa modificação"
        )
    pedido.status = "FINALIZADO"
    session.commit()
    return {
        "mensagem": f"Pedido número: {pedido.id} finalizado com sucesso",
        "pedido": pedido,
    }


@order_router.get("/pedido/{id_pedido}")
async def visualizar_pedido(
    id_pedido: int,
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token),
):
    """Visualiza os detalhes de um pedido específico.

    Args:
        id_pedido (int): O ID do pedido a ser visualizado.
        session (Session, optional): A sessão do banco de dados. Injetada por dependência.
        usuario (Usuario, optional): O usuário autenticado. Injetado por dependência.

    Raises:
        HTTPException: Se o pedido não for encontrado.
        HTTPException: Se o usuário não tiver autorização para acessar o pedido.

    Returns:
        dict: Os detalhes do pedido, incluindo a quantidade de itens.
    """
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(
            status_code=401, detail="Você não tem autorização para acessar este pedido"
        )
    return {"quantidade_itens_pedido": len(pedido.itens), "pedido": pedido}


# Visualizar todos os pedidos de um usuário
@order_router.get("/listar/pedidos-usuario", response_model=List[ResponsePedidoSchema])
async def listar_pedidos(
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token),
):
    """Lista todos os pedidos de um usuário específico.

    Args:
        session (Session, optional): A sessão do banco de dados. Injetada por dependência.
        usuario (Usuario, optional): O usuário autenticado. Injetado por dependência.

    Returns:
        List[ResponsePedidoSchema]: Uma lista de pedidos do usuário. Retorna uma lista vazia se não houver pedidos.
    """
    pedidos = session.query(Pedido).filter(Pedido.usuario == usuario.id).all()
    if not pedidos:
        # Garante que uma lista vazia seja retornada se não houver pedidos
        return []
    return pedidos  # Retorna a lista de objetos Pedido diretamente.
