# dashboard_app.py
import streamlit as st
import httpx
import os
import logging
from api_client import decode_jwt # Assumindo que esta função decode_jwt está em api_client.py
# from datetime import datetime, timedelta # Necessário para verificar a expiração do token, se quiser

# Configuração de logging
logging.basicConfig(level=logging.INFO)

# Caminhos para salvar os tokens
TOKEN_PATH = os.path.join(os.path.dirname(__file__), "access_token.txt")
REFRESH_TOKEN_PATH = os.path.join(os.path.dirname(__file__), "refresh_token.txt")
API_URL = "http://localhost:8000" # URL base do seu backend FastAPI

# --- Funções para ler e salvar tokens ---

@st.cache_data
def cached_token():
    """
    Lê o access token do arquivo.
    Usa st.cache_data para evitar leituras repetidas desnecessárias.
    """
    try:
        with open(TOKEN_PATH, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        logging.info(f"Arquivo '{TOKEN_PATH}' não encontrado. Token não disponível.")
        return None
    except Exception as e:
        logging.error(f"Erro ao obter access token do cache: {e}")
        return None

@st.cache_data
def cached_refresh_token():
    """
    Lê o refresh token do arquivo.
    Usa st.cache_data para evitar leituras repetidas desnecessárias.
    """
    try:
        with open(REFRESH_TOKEN_PATH, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        logging.info(f"Arquivo '{REFRESH_TOKEN_PATH}' não encontrado. Refresh Token não disponível.")
        return None
    except Exception as e:
        logging.error(f"Erro ao obter refresh token do cache: {e}")
        return None

def save_tokens(access_token: str, refresh_token: str):
    """
    Salva ambos os tokens (access e refresh) em arquivos separados.
    """
    try:
        with open(TOKEN_PATH, "w") as f:
            f.write(access_token)
        with open(REFRESH_TOKEN_PATH, "w") as f:
            f.write(refresh_token)
        logging.info("Tokens (access e refresh) salvos com sucesso.")
    except IOError as e:
        logging.error(f"Erro ao salvar tokens: {e}")
        st.error("Erro ao persistir tokens. Por favor, tente novamente.")

def clear_tokens():
    """
    Remove os arquivos de token para efetivar o logout ou quando a sessão expira.
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
    Tenta usar o refresh token para obter um novo access token.
    Retorna True se conseguir, False caso contrário.
    """
    refresh_t = cached_refresh_token()
    if not refresh_t:
        logging.warning("Refresh token não disponível. Não é possível renovar.")
        clear_tokens() # Limpa tudo se não há refresh token para forçar login
        return False

    try:
        logging.info("Tentando renovar o access token...")
        # Faz a requisição ao endpoint de renovação do backend
        # Ajuste a URL se seu endpoint de refresh token for diferente de /auth/refresh-token
        response = httpx.post(
            f"{API_URL}/auth/refresh-token",
            headers={"Authorization": f"Bearer {refresh_t}"}
        )
        response.raise_for_status() # Levanta erro para status 4xx/5xx

        novo_access_token = response.json().get("access_token")
        if novo_access_token:
            # Salva apenas o novo access token (o refresh token não muda neste fluxo)
            with open(TOKEN_PATH, "w") as f:
                f.write(novo_access_token)
            # Limpa o cache do Streamlit para que cached_token() leia o novo valor
            cached_token.clear()
            logging.info("Access token renovado e atualizado no arquivo.")
            return True
        else:
            logging.error("Resposta de renovação não continha um novo access_token.")
            clear_tokens()
            return False
    except httpx.HTTPStatusError as err:
        logging.error(f"Falha na renovação do token ({err.response.status_code}): {err}")
        st.error("Sua sessão expirou. Por favor, faça login novamente.")
        clear_tokens() # Limpa tokens se a renovação falhar
        return False
    except Exception as e:
        logging.error(f"Erro inesperado durante a renovação do token: {e}")
        clear_tokens()
        return False

# Função para realizar requisições à API com lógica de renovação
def api_request(method: str, endpoint: str, json_data: dict = None):
    """
    Realiza uma requisição HTTP para o backend FastAPI, incluindo autenticação
    e lógica de renovação de token em caso de expiração.
    """
    max_retries = 2 # Tentar a requisição original e mais uma vez após renovar
    for attempt in range(max_retries):
        token = cached_token()
        
        if not token:
            # Se não há token, e não é a primeira tentativa, algo deu errado
            if attempt > 0:
                logging.error("Token não encontrado após tentativa de renovação.")
                st.error("Sua sessão expirou. Por favor, faça login novamente.")
                st.session_state["logado"] = False
                st.rerun()
                return None
            
            # Na primeira tentativa, se não há token, tenta renovar (se houver refresh token)
            logging.info("Nenhum access token disponível. Tentando renovar.")
            if refresh_access_token_and_retry():
                token = cached_token() # Pega o token recém-renovado
                if not token: # Se mesmo assim não conseguir o token, falha
                    st.error("Falha ao obter novo token após renovação. Faça login novamente.")
                    st.session_state["logado"] = False
                    st.rerun()
                    return None
            else:
                # Se não puder renovar (sem refresh token ou erro), falha no login
                st.error("Não foi possível obter um token válido. Faça login novamente.")
                st.session_state["logado"] = False
                st.rerun()
                return None

        headers = {"Authorization": f"Bearer {token}"}
        url = f"{API_URL}{endpoint}"

        try:
            logging.info(f"Fazendo requisição: {method} {url}")
            response = httpx.request(method, url, json=json_data, headers=headers)
            response.raise_for_status() # Levanta um erro para status 4xx/5xx
            return response.json()
        except httpx.HTTPStatusError as err:
            # Se for um erro 401 (Unauthorized) e ainda há tentativas, tenta renovar
            if err.response.status_code == 401 and attempt < max_retries - 1:
                logging.warning("Access token expirado/inválido (401). Tentando renovar...")
                if refresh_access_token_and_retry():
                    # Se renovado com sucesso, o loop continuará para a próxima tentativa
                    continue
                else:
                    # Se não puder renovar, não há mais tentativas
                    st.error("Sessão expirou. Por favor, faça login novamente.")
                    st.session_state["logado"] = False
                    st.rerun()
                    return None
            else:
                # Outros erros HTTP ou 401 após todas as tentativas
                logging.error(f"Erro HTTP {err.response.status_code} na requisição para {endpoint}: {err}")
                st.error(f"Erro ao realizar a requisição: {err.details.get('detail', str(err))}")
                return None
        except Exception as e:
            logging.error(f"Erro inesperado ao realizar a requisição para {endpoint}: {e}")
            st.error(f"Erro inesperado: {e}")
            return None
    return None # Deve ser inalcançável se max_retries é 2 e a lógica funciona

# --- Funções do Formulário de Login ---
def login_form():
    """
    Exibe o formulário de login para o usuário.
    """
    st.title("Login")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if login_backend(email, senha): # Chama a função de login que interage com o backend
            st.session_state["logado"] = True
            st.rerun()

def login_backend(email, senha):
    """
    Faz a requisição de login ao backend e salva os tokens.
    """
    try:
        response = httpx.post(
            f"{API_URL}/auth/login", json={"email": email, "senha": senha}
        )
        response.raise_for_status() # Levanta erro para status 4xx/5xx
        
        tokens = response.json()
        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")
        
        if access_token and refresh_token:
            save_tokens(access_token, refresh_token)
            logging.info("Login bem-sucedido e tokens salvos.")
            return True
        else:
            st.error("Resposta do login incompleta (tokens ausentes).")
            return False
    except httpx.HTTPStatusError as err:
        logging.error(f"Erro no login ({err.response.status_code}): {err}")
        detail = err.response.json().get("detail", "Credenciais inválidas")
        st.error(f"Erro no login: {detail}")
        return False
    except Exception as e:
        logging.error(f"Erro inesperado durante o login: {e}")
        st.error("Erro inesperado durante o login. Por favor, tente novamente.")
        return False

# --- Funções do Dashboard ---
def criar_pedido():
    """
    Interface para criar um novo pedido.
    """
    st.subheader("Criar Novo Pedido")
    # Para criar um pedido, precisamos do ID do usuário logado
    # O ID do usuário está no payload do access token
    token = cached_token()
    if token:
        try:
            # Decodifica o JWT para obter o 'sub' (subject/ID do usuário)
            usuario_id = decode_jwt(token)
            if usuario_id:
                data = {"id_usuario": int(usuario_id)}
                result = api_request("POST", "/pedidos/pedido", json_data=data)
                if result:
                    st.success(result.get("mensagem", "Pedido criado com sucesso!"))
            else:
                st.warning("Não foi possível obter o ID do usuário do token.")
        except Exception as e:
            logging.error(f"Erro ao decodificar token para criar pedido: {e}")
            st.error("Erro ao criar pedido: Token inválido ou expirado.")
    else:
        st.warning("Faça login para criar um pedido.")


def listar_pedidos():
    """
    Lista os pedidos do usuário autenticado.
    """
    st.subheader("Seus Pedidos")
    try:
        # Chamada CORRIGIDA para o endpoint /pedidos/listar/pedidos-usuario
        # A api_request já adiciona a URL base e o Bearer token
        result = api_request("GET", "/pedidos/listar/pedidos-usuario")
        if result:
            pedidos = result.get("pedidos", []) # Garante que 'pedidos' seja uma lista, mesmo se vazio
            if not pedidos:
                st.info("Você não tem nenhum pedido registrado.")
            else:
                for pedido in pedidos:
                    st.write(f"ID: {pedido['id']} | Status: {pedido['status']}")
        else:
            st.info("Nenhum pedido foi retornado ou houve um erro.")
    except Exception as e:
        logging.error(f"Erro ao listar pedidos: {e}")
        st.error("Erro ao listar pedidos.")

def adicionar_item_pedido():
    """
    Interface para adicionar um item detalhado a um pedido existente.
    """
    st.subheader("Adicionar Item ao Pedido")
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
        else:
            st.warning("Por favor, preencha todos os campos do item.")

def modificar_item_pedido(endpoint_acao: str):
    """
    Interface genérica para modificar (remover) itens de um pedido.
    Agora usada especificamente para 'remover-item'.
    """
    st.subheader(f"{endpoint_acao.replace('-', ' ').capitalize()} Item do Pedido")
    id_pedido = st.text_input("ID do Pedido:", key=endpoint_acao + "_id")
    item = st.text_input("Nome do Item:", key=endpoint_acao + "_item") # Para remover, basta o nome do item

    if st.button("Confirmar", key=endpoint_acao + "_btn"):
        if id_pedido and item:
            try:
                # Fetch the order status to check if modification is allowed
                order = api_request("GET", f"/pedidos/pedido/{id_pedido}")
                if order and order.get("status") in ["FINALIZADO", "CANCELADO"]:
                    st.error("Não é possível remover itens de pedidos FINALIZADO ou CANCELADO.")
                    return

                data = {"item": item} # Para remover item, o backend geralmente espera o nome
                result = api_request(
                    "POST", f"/pedidos/pedido/{endpoint_acao}/{id_pedido}", json_data=data
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
    Interface para finalizar ou cancelar um pedido.
    """
    st.subheader(f"{acao.capitalize()} Pedido")
    id_pedido = st.text_input(
        f"ID do Pedido para {acao.capitalize()}:", key=f"{acao}_id"
    )
    if st.button(f"{acao.capitalize()} Pedido", key=f"{acao}_btn"):
        if id_pedido:
            try:
                # O endpoint já está com o prefixo '/pedidos'
                # Ex: /pedidos/pedido/finalizar/{id_pedido}
                result = api_request("POST", f"/pedidos/pedido/{acao}/{id_pedido}")
                if result:
                    st.success(f"Pedido {acao} com sucesso.")
            except Exception as e:
                logging.error(f"Erro ao {acao} pedido '{id_pedido}': {e}")
                st.error(f"Erro ao {acao} pedido.")
        else:
            st.warning("Preencha o ID do Pedido.")

def menu_dashboard():
    """
    Exibe o menu lateral e as interfaces para as ações do dashboard.
    """
    st.title("Dashboard de Pedidos")
    
    # Adicionar botão de Logout
    if st.sidebar.button("Sair"):
        clear_tokens()
        st.session_state["logado"] = False
        st.rerun()

    menu = [
        "Criar Pedido",
        "Listar Pedidos",
        "Adicionar Item", # Agora com detalhes
        "Remover Item", # Apenas ID do item
        "Finalizar Pedido",
        "Cancelar Pedido",
    ]
    escolha = st.sidebar.selectbox("Escolha uma ação", menu)

    # Renderiza a interface de acordo com a escolha do menu
    if escolha == "Criar Pedido":
        criar_pedido()
    elif escolha == "Listar Pedidos":
        listar_pedidos()
    elif escolha == "Adicionar Item":
        adicionar_item_pedido() # Chama a nova função
    elif escolha == "Remover Item":
        modificar_item_pedido("remover-item") # Mantém a função genérica para remover
    elif escolha == "Finalizar Pedido":
        mudar_status_pedido("finalizar")
    elif escolha == "Cancelar Pedido":
        mudar_status_pedido("cancelar")


def main():
    """
    Função principal do aplicativo Streamlit.
    Gerencia o estado de login e exibe o formulário de login ou o dashboard.
    """
    # Inicializa o estado 'logado' se não existir
    if "logado" not in st.session_state:
        st.session_state["logado"] = False

    # Verifica se já há tokens persistidos para tentar logar automaticamente
    if not st.session_state["logado"] and cached_token() and cached_refresh_token():
        logging.info("Tokens encontrados. Tentando revalidar sessão.")
        # Se há tokens, considera o usuário logado para tentar uma requisição
        # A próxima api_request (por exemplo, ao listar pedidos) tentará renovar
        st.session_state["logado"] = True
        # st.rerun() # Opcional: pode ser útil para recarregar a UI após "auto-login"

    # Exibe o formulário de login ou o dashboard
    if not st.session_state["logado"]:
        login_form()
    else:
        menu_dashboard()


if __name__ == "__main__":
    main()

