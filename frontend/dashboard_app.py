# dashboard_app.py
import streamlit as st
import httpx
import os
import logging
from api_client import decode_jwt

# Configuração de logging
logging.basicConfig(level=logging.INFO)


def api_request(method, endpoint, json_data=None):
    token = cached_token()  # Obtém o token do arquivo token.txt
    if not token:
        logging.error("Token não encontrado!")
        st.error("Não foi possível obter um token válido.")
        return None  # Se o token não for encontrado, retorna None
    print(f"Token obtido: {token}")  # Verifique se o token é válido e está sendo lido corretamente
    
    headers = {"Authorization": f"Bearer {token}"}  # Inclui o token no cabeçalho

    try:
        url = f"{API_URL}{endpoint}"
        response = httpx.request(method, url, json=json_data, headers=headers)
        response.raise_for_status()  # Levanta um erro se a resposta for 4xx ou 5xx
        return response.json()  # Retorna o conteúdo JSON da resposta
    except httpx.HTTPStatusError as err:
        logging.error(f"Erro HTTP na requisição para {endpoint}: {err}")
        st.error(f"Erro ao realizar a requisição: {err}")
        return None
    except Exception as e:
        logging.error(f"Erro ao realizar a requisição para {endpoint}: {e}")
        st.error(f"Erro ao realizar a requisição: {e}")
        return None

# Shared path for the token file
TOKEN_PATH = os.path.join(os.path.dirname(__file__), "..", "access_token.txt")
API_URL = "http://localhost:8000"


# Função para realizar login
def login(email, senha):
    try:
        response = httpx.post(
            f"{API_URL}/auth/login", json={"email": email, "senha": senha}
        )
        response.raise_for_status()
        token = response.json()["access_token"]
        with open(TOKEN_PATH, "w") as f:
            f.write(token)
        return True
    except Exception as e:
        st.error("Erro no login: " + str(e))
        return False


# Tela de login
def login_form():
    st.title("Login")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if login(email, senha):
            st.session_state["logado"] = True
            st.rerun()


# Recupera o token do arquivo
@st.cache_data
def cached_token():
    try:
        with open(TOKEN_PATH, "r") as f:
            return f.read().strip()
    except Exception as e:
        logging.error(f"Erro ao obter token: {e}")
        return None


def criar_pedido():
    usuario_id = decode_jwt(cached_token())
    if usuario_id:
        data = {"id_usuario": int(usuario_id)}
        try:
            result = api_request("POST", "/pedidos/pedido", json_data=data)
            if result:
                st.success(result.get("mensagem", "Pedido criado com sucesso!"))
        except Exception as e:
            logging.error(f"Erro ao criar pedido: {e}")
            st.error("Erro ao criar pedido.")


def listar_pedidos():
    try:
        result = api_request("GET", "/pedidos/listar/pedidos-usuario")
        if result:
            for pedido in result:
                st.write(f"ID: {pedido['id']} | Status: {pedido['status']}")
    except Exception as e:
        logging.error(f"Erro ao listar pedidos: {e}")
        st.error("Erro ao listar pedidos.")


def adicionar_item_pedido():
    id_pedido = st.text_input("ID do Pedido:", key="adicionar_item_id_pedido")
    quantidade = st.number_input("Quantidade:", min_value=1, key="adicionar_item_quantidade")
    sabor = st.text_input("Sabor:", key="adicionar_item_sabor")
    tamanho = st.selectbox("Tamanho:", ["Pequeno", "Médio", "Grande"], key="adicionar_item_tamanho")
    preco_unitario = st.number_input("Preço Unitário:", min_value=0.0, format="%.2f", key="adicionar_item_preco_unitario")

    if st.button("Adicionar Item", key="adicionar_item_btn"):
        if id_pedido and quantidade and sabor and tamanho and preco_unitario:
            try:
                # Fetch the order status
                order = api_request("GET", f"/pedidos/pedido/{id_pedido}")
                if order and order.get("status") in ["FINALIZADO", "CANCELADO"]:
                    st.error("Não é possível adicionar itens a pedidos FINALIZADO ou CANCELADO.")
                    return

                # Proceed with adding the item
                data = {
                    "quantidade": quantidade,
                    "sabor": sabor,
                    "tamanho": tamanho,
                    "preco_unitario": preco_unitario,
                }
                result = api_request(
                    "POST", f"/pedidos/pedido/adicionar-item/{id_pedido}", json_data=data
                )
                if result:
                    st.success("Item adicionado com sucesso ao pedido.")
            except Exception as e:
                logging.error(f"Erro ao adicionar item: {e}")
                st.error("Erro ao adicionar item.")

def remover_item_pedido():
    id_item_pedido = st.text_input("ID do Item do Pedido:", key="remover_item_id_item_pedido")

    if st.button("Remover Item", key="remover_item_btn"):
        if id_item_pedido:
            try:
                # Proceed with removing the item
                result = api_request(
                    "DELETE", f"/pedidos/pedido/remover-item/{id_item_pedido}"
                )
                if result:
                    st.success("Item removido com sucesso do pedido.")
                else:
                    st.error("Erro ao remover item. Verifique se o ID do item está correto.")
            except Exception as e:
                logging.error(f"Erro ao remover item: {e}")
                st.error("Erro ao remover item.")

def mudar_status_pedido(acao):
    id_pedido = st.text_input(
        f"ID do Pedido para {acao.capitalize()}:", key=acao + "_id"
    )
    if st.button(f"{acao.capitalize()} Pedido", key=acao + "_btn"):
        if id_pedido:
            try:
                result = api_request("POST", f"/pedidos/pedido/{acao}/{id_pedido}")
                if result:
                    st.success(f"Pedido {acao} com sucesso.")
            except Exception as e:
                logging.error(f"Erro ao {acao} pedido: {e}")
                st.error(f"Erro ao {acao} pedido.")


def menu_dashboard():
    st.title("Dashboard de Pedidos")
    menu = [
        "Criar Pedido",
        "Listar Pedidos",
        "Adicionar Item",
        "Remover Item",
        "Finalizar Pedido",
        "Cancelar Pedido",
    ]
    escolha = st.sidebar.selectbox("Escolha uma ação", menu)

    if escolha == "Criar Pedido":
        criar_pedido()
    elif escolha == "Listar Pedidos":
        listar_pedidos()
    elif escolha == "Adicionar Item":
        adicionar_item_pedido()
    elif escolha == "Remover Item":
        remover_item_pedido()
    elif escolha == "Finalizar Pedido":
        mudar_status_pedido("finalizar")
    elif escolha == "Cancelar Pedido":
        mudar_status_pedido("cancelar")


def main():
    if "logado" not in st.session_state:
        st.session_state["logado"] = False

    if not st.session_state["logado"]:
        login_form()
    else:
        menu_dashboard()


if __name__ == "__main__":
    main()
