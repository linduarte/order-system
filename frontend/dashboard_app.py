# dashboard_app.py

import streamlit as st
import httpx
import os
import logging
from api_client import decode_jwt

# Configuração de logging
logging.basicConfig(level=logging.INFO)

# Caminhos para salvar os tokens
TOKEN_PATH = os.path.join(os.path.dirname(__file__), "access_token.txt")
REFRESH_TOKEN_PATH = os.path.join(os.path.dirname(__file__), "refresh_token.txt")
API_URL = "http://localhost:8000"  # URL base do backend FastAPI


# Função para aplicar a fonte Victor Mono Nerd Font
def inject_custom_font():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Victor+Mono&display=swap');

        html, body, [class*="css"]  {
            font-family: 'Victor Mono', monospace;
            font-size: 16px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# --- Funções para leitura e salvamento de tokens ---


@st.cache_data
def cached_token():
    """
    Retorna o access token armazenado em arquivo local, se existir.
    Utiliza cache para evitar leituras frequentes do disco.
    """
    try:
        with open(TOKEN_PATH, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        logging.info("Arquivo de access token não encontrado.")
        return None
    except Exception as e:
        logging.error(f"Erro ao ler access token: {e}")
        return None


@st.cache_data
def cached_refresh_token():
    """
    Retorna o refresh token armazenado em arquivo local, se existir.
    Utiliza cache para evitar leituras frequentes do disco.
    """
    try:
        with open(REFRESH_TOKEN_PATH, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        logging.info("Arquivo de refresh token não encontrado.")
        return None
    except Exception as e:
        logging.error(f"Erro ao ler refresh token: {e}")
        return None


def save_tokens(access_token: str, refresh_token: str):
    """
    Salva os tokens de acesso e de atualização em arquivos locais.
    """
    try:
        with open(TOKEN_PATH, "w") as f:
            f.write(access_token)
        with open(REFRESH_TOKEN_PATH, "w") as f:
            f.write(refresh_token)
        logging.info("Tokens salvos com sucesso.")
    except IOError as e:
        logging.error(f"Erro ao salvar tokens: {e}")
        st.error("Erro ao salvar os tokens. Tente novamente.")


def clear_tokens():
    """
    Remove os arquivos de tokens, efetivamente desconectando o usuário.
    """
    try:
        if os.path.exists(TOKEN_PATH):
            os.remove(TOKEN_PATH)
        if os.path.exists(REFRESH_TOKEN_PATH):
            os.remove(REFRESH_TOKEN_PATH)
        logging.info("Tokens removidos com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao limpar tokens: {e}")


def refresh_access_token_and_retry():
    """
    Realiza uma solicitação para atualizar o access token usando o refresh token.

    Returns:
        bool: True se o token foi renovado com sucesso, False caso contrário.
    """
    refresh_t = cached_refresh_token()
    if not refresh_t:
        logging.warning("Refresh token ausente.")
        clear_tokens()
        return False

    try:
        response = httpx.post(
            f"{API_URL}/auth/refresh-token",
            headers={"Authorization": f"Bearer {refresh_t}"},
        )
        response.raise_for_status()

        novo_access_token = response.json().get("access_token")
        if novo_access_token:
            with open(TOKEN_PATH, "w") as f:
                f.write(novo_access_token)
            cached_token.clear()
            logging.info("Access token renovado com sucesso.")
            return True
        else:
            logging.error("Token de acesso não retornado.")
            clear_tokens()
            return False
    except httpx.HTTPStatusError as err:
        logging.error(f"Erro HTTP na renovação do token: {err}")
        st.error("Sessão expirada. Faça login novamente.")
        clear_tokens()
        return False
    except Exception as e:
        logging.error(f"Erro ao renovar token: {e}")
        clear_tokens()
        return False


def api_request(method: str, endpoint: str, json_data: dict = None):
    """
    Realiza uma requisição à API com autenticação e lógica de renovação de token.

    Args:
        method (str): Método HTTP (GET, POST, etc.)
        endpoint (str): Caminho do recurso da API.
        json_data (dict, optional): Dados a serem enviados no corpo da requisição.

    Returns:
        dict or None: Resposta JSON da API ou None em caso de erro.
    """
    max_retries = 2
    for attempt in range(max_retries):
        token = cached_token()
        if not token and attempt == 0 and refresh_access_token_and_retry():
            token = cached_token()

        if not token:
            st.error("Sessão expirada. Faça login novamente.")
            st.session_state["logado"] = False
            st.rerun()
            return None

        headers = {"Authorization": f"Bearer {token}"}
        url = f"{API_URL}{endpoint}"
        try:
            response = httpx.request(method, url, json=json_data, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as err:
            if err.response.status_code == 401 and attempt < max_retries - 1:
                logging.warning("Token expirado. Tentando renovar...")
                if refresh_access_token_and_retry():
                    continue
                else:
                    st.error("Sessão expirada. Faça login novamente.")
                    st.session_state["logado"] = False
                    st.rerun()
                    return None
            else:
                st.error(f"Erro na requisição: {err}")
                return None
        except Exception as e:
            logging.error(f"Erro inesperado na requisição: {e}")
            st.error("Erro inesperado ao comunicar com o servidor.")
            return None
    return None


# --- UI de Login ---


def login_form():
    """
    Renderiza o formulário de login na interface Streamlit.
    """
    st.title("Login")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if login_backend(email, senha):
            st.session_state["logado"] = True
            st.rerun()


def login_backend(email, senha):
    """
    Realiza o login no backend e armazena os tokens recebidos.

    Args:
        email (str): Email do usuário.
        senha (str): Senha do usuário.

    Returns:
        bool: True se login for bem-sucedido, False caso contrário.
    """
    try:
        response = httpx.post(
            f"{API_URL}/auth/login", json={"email": email, "senha": senha}
        )
        response.raise_for_status()
        tokens = response.json()
        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")

        if access_token and refresh_token:
            save_tokens(access_token, refresh_token)
            logging.info("Login bem-sucedido.")
            return True
        else:
            st.error("Tokens ausentes na resposta.")
            return False
    except httpx.HTTPStatusError as err:
        detail = err.response.json().get("detail", "Erro ao fazer login.")
        st.error(f"Erro: {detail}")
        return False
    except Exception as e:
        logging.error(f"Erro no login: {e}")
        st.error("Erro inesperado ao fazer login.")
        return False


# --- Funções do Dashboard ---


def criar_pedido():
    """
    Interface Streamlit para criar um novo pedido vinculado ao usuário autenticado.
    Utiliza o access token para recuperar o ID do usuário via decode_jwt().
    """
    st.subheader("Criar Novo Pedido")
    token = cached_token()
    if token:
        try:
            usuario_id = decode_jwt(token)
            if usuario_id:
                data = {"id_usuario": int(usuario_id)}
                result = api_request("POST", "/pedidos/pedido", json_data=data)
                if result:
                    st.success(result.get("mensagem", "Pedido criado com sucesso!"))
            else:
                st.warning("Não foi possível obter o ID do usuário do token.")
        except Exception as e:
            logging.error(f"Erro ao criar pedido: {e}")
            st.error("Erro ao criar pedido.")
    else:
        st.warning("Faça login para criar um pedido.")


def listar_pedidos():
    """
    Lista os pedidos do usuário autenticado na interface.
    """
    st.subheader("Seus Pedidos")
    try:
        result = api_request("GET", "/pedidos/listar/pedidos-usuario")
        if result:
            pedidos = result.get("pedidos", [])
            if not pedidos:
                st.info("Você não tem nenhum pedido registrado.")
            else:
                for pedido in pedidos:
                    st.write(f"ID: {pedido['id']} | Status: {pedido['status']}")
        else:
            st.info("Nenhum pedido encontrado.")
    except Exception as e:
        logging.error(f"Erro ao listar pedidos: {e}")
        st.error("Erro ao listar pedidos.")


def adicionar_item_pedido():
    """
    Interface para adicionar um item a um pedido existente.
    Requer o ID do pedido e dados do item como sabor, tamanho, quantidade e preço.
    """
    st.subheader("Adicionar Item ao Pedido")
    id_pedido = st.text_input("ID do Pedido:", key="adicionar_item_id_pedido")
    quantidade = st.number_input(
        "Quantidade:", min_value=1, key="adicionar_item_quantidade"
    )
    sabor = st.text_input("Sabor:", key="adicionar_item_sabor")
    tamanho = st.selectbox(
        "Tamanho:", ["Pequeno", "Médio", "Grande"], key="adicionar_item_tamanho"
    )
    preco_unitario = st.number_input(
        "Preço Unitário:",
        min_value=0.0,
        format="%.2f",
        key="adicionar_item_preco_unitario",
    )

    if st.button("Adicionar Item", key="adicionar_item_btn"):
        if id_pedido and quantidade and sabor and tamanho and preco_unitario:
            try:
                order = api_request("GET", f"/pedidos/pedido/{id_pedido}")
                if order and order.get("status") in ["FINALIZADO", "CANCELADO"]:
                    st.error(
                        "Não é possível adicionar itens a pedidos FINALIZADO ou CANCELADO."
                    )
                    return

                data = {
                    "quantidade": quantidade,
                    "sabor": sabor,
                    "tamanho": tamanho,
                    "preco_unitario": preco_unitario,
                }
                result = api_request(
                    "POST",
                    f"/pedidos/pedido/adicionar-item/{id_pedido}",
                    json_data=data,
                )
                if result:
                    st.success("Item adicionado com sucesso ao pedido.")
            except Exception as e:
                logging.error(f"Erro ao adicionar item: {e}")
                st.error("Erro ao adicionar item.")
        else:
            st.warning("Por favor, preencha todos os campos do item.")


def modificar_item_pedido(endpoint_acao: str):
    """
    Interface genérica para ações sobre um item (como remoção), baseada em endpoint específico.

    Args:
        endpoint_acao (str): Ação do endpoint, como 'remover-item'.
    """
    st.subheader(f"{endpoint_acao.replace('-', ' ').capitalize()} Item do Pedido")
    id_pedido = st.text_input("ID do Pedido:", key=endpoint_acao + "_id")
    item = st.text_input("Nome do Item:", key=endpoint_acao + "_item")

    if st.button("Confirmar", key=endpoint_acao + "_btn"):
        if id_pedido and item:
            try:
                order = api_request("GET", f"/pedidos/pedido/{id_pedido}")
                if order and order.get("status") in ["FINALIZADO", "CANCELADO"]:
                    st.error(
                        "Não é possível modificar itens de pedidos FINALIZADO ou CANCELADO."
                    )
                    return

                data = {"item": item}
                result = api_request(
                    "POST",
                    f"/pedidos/pedido/{endpoint_acao}/{id_pedido}",
                    json_data=data,
                )
                if result:
                    st.success("Item atualizado com sucesso.")
            except Exception as e:
                logging.error(f"Erro ao modificar item: {e}")
                st.error("Erro ao modificar item.")
        else:
            st.warning("Preencha o ID do Pedido e o nome do Item.")


def mudar_status_pedido(acao: str):
    """
    Interface para mudar o status de um pedido (finalizar ou cancelar).

    Args:
        acao (str): Ação desejada - 'finalizar' ou 'cancelar'.
    """
    st.subheader(f"{acao.capitalize()} Pedido")
    id_pedido = st.text_input(
        f"ID do Pedido para {acao.capitalize()}:", key=f"{acao}_id"
    )
    if st.button(f"{acao.capitalize()} Pedido", key=f"{acao}_btn"):
        if id_pedido:
            try:
                result = api_request("POST", f"/pedidos/pedido/{acao}/{id_pedido}")
                if result:
                    st.success(f"Pedido {acao} com sucesso.")
            except Exception as e:
                logging.error(f"Erro ao {acao} pedido: {e}")
                st.error(f"Erro ao {acao} pedido.")
        else:
            st.warning("Preencha o ID do Pedido.")


def menu_dashboard():
    """
    Exibe o menu lateral do dashboard com opções de ações.
    Permite logout e redireciona para interfaces específicas com base na escolha.
    """
    st.title("Dashboard de Pedidos")

    if st.sidebar.button("Sair"):
        clear_tokens()
        st.session_state["logado"] = False
        st.rerun()

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
        modificar_item_pedido("remover-item")
    elif escolha == "Finalizar Pedido":
        mudar_status_pedido("finalizar")
    elif escolha == "Cancelar Pedido":
        mudar_status_pedido("cancelar")


def main():
    """
    Função principal do app. Controla o estado de login e navegação
    entre o formulário de login e o dashboard.
    """
    if "logado" not in st.session_state:
        st.session_state["logado"] = False

    if not st.session_state["logado"] and cached_token() and cached_refresh_token():
        logging.info("Tokens encontrados. Tentando revalidar sessão.")
        st.session_state["logado"] = True

    if not st.session_state["logado"]:
        login_form()
    else:
        menu_dashboard()


if __name__ == "__main__":
    main()
