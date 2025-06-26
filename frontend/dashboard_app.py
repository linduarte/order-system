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

# Caminho para salvar o token
TOKEN_PATH = os.path.join(os.path.dirname(__file__), "token.txt")
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
        result = api_request("GET", "/pedidos/listar")
        if result:
            for pedido in result:
                st.write(f"ID: {pedido['id']} | Status: {pedido['status']}")
    except Exception as e:
        logging.error(f"Erro ao listar pedidos: {e}")
        st.error("Erro ao listar pedidos.")


def modificar_item_pedido(endpoint):
    id_pedido = st.text_input("ID do Pedido:", key=endpoint + "_id")
    item = st.text_input("Nome do Item:", key=endpoint + "_item")
    if st.button("Confirmar", key=endpoint + "_btn"):
        if id_pedido and item:
            data = {"item": item}
            try:
                result = api_request(
                    "POST", f"/pedidos/pedido/{endpoint}/{id_pedido}", json_data=data
                )
                if result:
                    st.success("Item atualizado com sucesso.")
            except Exception as e:
                logging.error(f"Erro ao modificar item: {e}")
                st.error("Erro ao modificar item.")


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
        modificar_item_pedido("adicionar-item")
    elif escolha == "Remover Item":
        modificar_item_pedido("remover-item")
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
