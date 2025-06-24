import streamlit as st
import httpx
import os
import base64
import json


# --- Configurações da API e do Token ---
API_URL = "http://localhost:8000"
# Caminho para o arquivo do token. Para Streamlit local, isso funciona.
# Para deploy, considere variáveis de ambiente ou upload de arquivos.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH = os.path.join(BASE_DIR, "token.txt")

# Ignorar Ctrl+C não é necessário ou aplicável da mesma forma no Streamlit,
# pois ele é executado via `streamlit run` e o servidor gerencia o ciclo de vida.
# signal.signal(signal.SIGINT, signal.SIG_IGN)

# --- Funções Auxiliares (adaptadas para Streamlit) ---

def decode_jwt(token):
    """Decodifica um token JWT e retorna seu payload."""
    try:
        payload_base64 = token.split(".")[1]
        # Preencher o base64 se necessário
        padding = 4 - len(payload_base64) % 4
        if padding != 4:
            payload_base64 += "=" * padding
        decoded = base64.urlsafe_b64decode(payload_base64)
        return json.loads(decoded)
    except Exception as e:
        st.error(f"[ERRO] Falha ao decodificar token: {e}")
        return {}

# Função get_token_from_file agora é opcional se o token for armazenado em session_state
def get_token_from_file():
    """Busca o token do arquivo local."""
    if not os.path.exists(TOKEN_PATH):
        # st.warning("Token file not found. Please log in.") # Use st.warning for this case
        return None
    try:
        with open(TOKEN_PATH, "r") as f:
            token = f.read().strip()
        return token
    except Exception as e:
        st.error(f"Erro ao ler o arquivo do token: {e}")
        return None

# A função get_token agora prioriza session_state
def get_token():
    """Obtém o token, priorizando o session_state do Streamlit."""
    if 'auth_token' in st.session_state and st.session_state.auth_token:
        return st.session_state.auth_token
    # Se não estiver no session_state, tenta do arquivo (para persistência entre execuções)
    file_token = get_token_from_file()
    if file_token:
        st.session_state.auth_token = file_token
        return file_token
    return None

def get_user_id():
    """Obtém o ID do usuário do token JWT."""
    token = get_token()
    if not token:
        return None
    payload = decode_jwt(token)
    return int(payload.get("sub")) if payload.get("sub") else None

def api_post_streamlit(endpoint, payload=None):
    """
    Função genérica para requisições POST à API, adaptada para Streamlit.
    Retorna (True, resultado_json) em sucesso ou (False, mensagem_de_erro) em falha.
    Exibe mensagens de erro diretamente no Streamlit.
    """
    token = get_token()
    if not token:
        st.warning("Token ausente. Por favor, faça login.")
        return False, "Token ausente"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = httpx.post(f"{API_URL}{endpoint}", json=payload, headers=headers)
        response.raise_for_status() # Lança exceção para códigos de status 4xx/5xx
        return True, response.json()
    except httpx.HTTPStatusError as err:
        error_msg = f"Erro da API ({err.response.status_code}): {err.response.text}"
        st.error(error_msg)
        return False, error_msg
    except httpx.RequestError as err: # Captura erros de rede, DNS, etc.
        error_msg = f"Erro de rede ao conectar à API: {err}"
        st.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Erro inesperado: {str(e)}"
        st.error(error_msg)
        return False, error_msg

def api_get_streamlit(endpoint):
    """
    Função genérica para requisições GET à API, adaptada para Streamlit.
    Retorna (True, resultado_json) em sucesso ou (False, mensagem_de_erro) em falha.
    Exibe mensagens de erro diretamente no Streamlit.
    """
    token = get_token()
    if not token:
        st.warning("Token ausente. Por favor, faça login.")
        return False, "Token ausente"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = httpx.get(f"{API_URL}{endpoint}", headers=headers)
        response.raise_for_status()
        return True, response.json()
    except httpx.HTTPStatusError as err:
        error_msg = f"Erro da API ({err.response.status_code}): {err.response.text}"
        st.error(error_msg)
        return False, error_msg
    except httpx.RequestError as err:
        error_msg = f"Erro de rede ao conectar à API: {err}"
        st.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Erro inesperado: {str(e)}"
        st.error(error_msg)
        return False, error_msg

# --- Lógica do Dashboard Streamlit ---

def main():
    st.set_page_config(layout="centered", page_title="Dashboard de Pedidos")
    
    # --- INÍCIO: Adição do CSS para Nerd Font ---
    st.markdown("""
        <style>
        /* Importa a fonte. Certifique-se de que o caminho para o arquivo da fonte esteja correto.
           Para uso local com Streamlit, os arquivos na pasta 'static' ou no mesmo diretório
           do script podem ser referenciados assim. */
        @font-face {
            font-family: 'HackNerdFont';
            src: url('https://raw.githubusercontent.com/ryanoasis/nerd-fonts/HEAD/patched-fonts/Hack/Regular/HackNerdFont-Regular.ttf') format('truetype');
            font-weight: normal;
            font-style: normal;
            font-display: swap;
        }

        /* Aplica a fonte a todo o corpo da aplicação */
        body {
            font-family: 'HackNerdFont', monospace, sans-serif !important;
        }

        /* Você também pode aplicar a elementos específicos, por exemplo: */
        .stApp, .stTextInput, .stButton>button, .stText {
            font-family: 'HackNerdFont', monospace, sans-serif !important;
        }
        
        /* Ajusta o tamanho da fonte para melhor legibilidade com Nerd Fonts */
        html, body, [class*="st-emotion"], [class*="stMarkdown"] {
            font-size: 16px; /* Ajuste conforme necessário */
        }

        /* Estilos para os títulos */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'HackNerdFont', monospace, sans-serif !important;
        }
        </style>
        """, unsafe_allow_html=True)
    # --- FIM: Adição do CSS para Nerd Font ---

    st.title("Dashboard de Pedidos")

    # Inicializa o estado de autenticação e inputs
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'auth_token' not in st.session_state:
        st.session_state.auth_token = get_token_from_file() # Tenta carregar do arquivo na inicialização
        if st.session_state.auth_token:
            st.session_state.logged_in = True


    # --- Lógica de Login ---
    if not st.session_state.logged_in:
        st.subheader("Login")
        email = st.text_input("Email:", key="login_email") # Alterado de 'Usuário' para 'Email'
        senha = st.text_input("Senha:", type="password", key="login_password") # Alterado de 'password' para 'senha'

        if st.button("Entrar", type="primary"):
            if email and senha: # Usando email e senha
                try:
                    # Adaptado para o endpoint e payload do seu main.py
                    login_response = httpx.post(
                        f"{API_URL}/auth/login", # Endpoint corrigido
                        json={"email": email, "senha": senha} # Payload corrigido
                    )
                    login_response.raise_for_status()
                    token_data = login_response.json()
                    new_token = token_data.get("access_token")

                    if new_token:
                        st.session_state.auth_token = new_token
                        st.session_state.logged_in = True
                        st.success("Login bem-sucedido!")
                        # Opcional: Salvar o token no arquivo para persistência entre sessões
                        with open(TOKEN_PATH, "w") as f:
                            f.write(new_token)
                        # Re-executa o aplicativo para mostrar o dashboard
                        st.rerun() # Corrigido: st.experimental_rerun() para st.rerun()
                    else:
                        st.error("Resposta da API de login inválida: token 'access_token' não encontrado.")
                except httpx.HTTPStatusError as err:
                    st.error(f"Erro de login ({err.response.status_code}): {err.response.text}")
                except httpx.RequestError as err:
                    st.error(f"Erro de rede ao tentar fazer login: {err}")
                except Exception as e:
                    st.error(f"Erro inesperado durante o login: {str(e)}")
            else:
                st.warning("Por favor, preencha o email e a senha.")
        st.info("Você precisa fazer login para acessar o dashboard.")
        return # Para o resto do código do dashboard não ser executado antes do login


    # --- Dashboard Principal (visível apenas após o login) ---
    st.write("Bem-vindo ao seu dashboard interativo de gerenciamento de pedidos.")

    # Botão de Logout
    if st.button("Sair", type="secondary"):
        st.session_state.logged_in = False
        st.session_state.auth_token = None
        if os.path.exists(TOKEN_PATH):
            os.remove(TOKEN_PATH) # Remove o token salvo
        st.info("Você foi desconectado.")
        st.rerun() # Corrigido: st.experimental_rerun() para st.rerun()


    # Inicializa o estado da sessão para controlar inputs e mensagens
    if 'show_criar_pedido_input' not in st.session_state:
        st.session_state.show_criar_pedido_input = False
    if 'show_adicionar_item_input' not in st.session_state:
        st.session_state.show_adicionar_item_input = False
    if 'show_remover_item_input' not in st.session_state:
        st.session_state.show_remover_item_input = False
    if 'show_finalizar_pedido_input' not in st.session_state:
        st.session_state.show_finalizar_pedido_input = False
    if 'show_cancelar_pedido_input' not in st.session_state:
        st.session_state.show_cancelar_pedido_input = False
    
    # Área para exibir mensagens de sucesso/erro globais ou feedback
    message_placeholder = st.empty()


    # Função para redefinir todos os estados de input
    def reset_inputs_state():
        st.session_state.show_criar_pedido_input = False
        st.session_state.show_adicionar_item_input = False
        st.session_state.show_remover_item_input = False
        st.session_state.show_finalizar_pedido_input = False
        st.session_state.show_cancelar_pedido_input = False
        # Limpa os valores dos inputs se existirem
        if 'criar_pedido_user_id' in st.session_state:
            st.session_state.criar_pedido_user_id = ""
        if 'add_item_pedido_id' in st.session_state:
            st.session_state.add_item_pedido_id = ""
        if 'add_item_nome_item' in st.session_state:
            st.session_state.add_item_nome_item = ""
        if 'remove_item_pedido_id' in st.session_state:
            st.session_state.remove_item_pedido_id = ""
        if 'remove_item_nome_item' in st.session_state:
            st.session_state.remove_item_nome_item = ""
        if 'finalizar_pedido_id' in st.session_state:
            st.session_state.finalizar_pedido_id = ""
        if 'cancelar_pedido_id' in st.session_state:
            st.session_state.cancelar_pedido_id = ""


    # --- Botão Criar Pedido ---
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Criar Pedido", use_container_width=True):
            reset_inputs_state()
            st.session_state.show_criar_pedido_input = True
    with col2:
        if st.session_state.show_criar_pedido_input:
            user_id_str = st.text_input("ID do Usuário para o novo pedido:", key="criar_pedido_user_id")
            if st.button("Confirmar Criação", key="confirm_criar_pedido"):
                if user_id_str and user_id_str.isdigit():
                    user_id = int(user_id_str)
                    success, result = api_post_streamlit("/pedidos/pedido", payload={"id_usuario": user_id})
                    if success:
                        msg = result.get("mensagem", "Pedido criado com sucesso.")
                        message_placeholder.success(msg)
                    st.session_state.show_criar_pedido_input = False # Esconde o input após a ação
                else:
                    message_placeholder.error("ID do usuário inválido.")

    st.markdown("---") # Separador visual

    # --- Botão Listar Meus Pedidos ---
    if st.button("Listar Meus Pedidos", type="primary", use_container_width=True):
        reset_inputs_state()
        success, result = api_get_streamlit("/pedidos/listar/pedidos-usuario")
        if success:
            if result:
                st.subheader("Seus Pedidos:")
                for p in result:
                    st.write(f"**ID:** {p.get('id')} - **Status:** {p.get('status')} - **Itens:** {', '.join(p.get('itens', []))}")
            else:
                st.info("Nenhum pedido encontrado para o seu usuário.")

    st.markdown("---") # Separador visual

    # --- Botão Adicionar Item ---
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Adicionar Item", use_container_width=True):
            reset_inputs_state()
            st.session_state.show_adicionar_item_input = True
    with col2:
        if st.session_state.show_adicionar_item_input:
            pedido_id_add = st.text_input("ID do Pedido:", key="add_item_pedido_id")
            nome_item_add = st.text_input("Nome do Item:", key="add_item_nome_item")
            if st.button("Confirmar Adição", key="confirm_add_item"):
                if pedido_id_add and nome_item_add:
                    success, result = api_post_streamlit(
                        f"/pedidos/pedido/adicionar-item/{pedido_id_add}", payload={"item": nome_item_add}
                    )
                    if success:
                        message_placeholder.success(result.get("mensagem", "Item adicionado com sucesso."))
                    st.session_state.show_adicionar_item_input = False # Esconde o input após a ação
                else:
                    message_placeholder.error("Por favor, preencha o ID do pedido e o nome do item.")

    st.markdown("---") # Separador visual

    # --- Botão Remover Item ---
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Remover Item", use_container_width=True):
            reset_inputs_state()
            st.session_state.show_remover_item_input = True
    with col2:
        if st.session_state.show_remover_item_input:
            pedido_id_remove = st.text_input("ID do Pedido:", key="remove_item_pedido_id")
            nome_item_remove = st.text_input("Nome do Item:", key="remove_item_nome_item")
            if st.button("Confirmar Remoção", key="confirm_remove_item"):
                if pedido_id_remove and nome_item_remove:
                    success, result = api_post_streamlit(
                        f"/pedidos/pedido/remover-item/{pedido_id_remove}", payload={"item": nome_item_remove}
                    )
                    if success:
                        message_placeholder.success(result.get("mensagem", "Item removido com sucesso."))
                    st.session_state.show_remover_item_input = False # Esconde o input após a ação
                else:
                    message_placeholder.error("Por favor, preencha o ID do pedido e o nome do item.")

    st.markdown("---") # Separador visual

    # --- Botão Finalizar Pedido ---
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Finalizar Pedido", type="secondary", use_container_width=True):
            reset_inputs_state()
            st.session_state.show_finalizar_pedido_input = True
    with col2:
        if st.session_state.show_finalizar_pedido_input:
            pedido_id_finalizar = st.text_input("ID do Pedido a Finalizar:", key="finalizar_pedido_id")
            if st.button("Confirmar Finalização", key="confirm_finalizar_pedido"):
                if pedido_id_finalizar:
                    success, result = api_post_streamlit(f"/pedidos/pedido/finalizar/{pedido_id_finalizar}")
                    if success:
                        message_placeholder.success(result.get("mensagem", "Pedido finalizado com sucesso."))
                    st.session_state.show_finalizar_pedido_input = False # Esconde o input após a ação
                else:
                    message_placeholder.error("Por favor, preencha o ID do pedido.")

    st.markdown("---") # Separador visual

    # --- Botão Cancelar Pedido ---
    col1, col2 = st.columns([1, 3])
    with col1:
        # Removido type="danger" para usar o estilo padrão, pois "danger" não é um tipo válido para st.button
        if st.button("Cancelar Pedido", use_container_width=True):
            reset_inputs_state()
            st.session_state.show_cancelar_pedido_input = True
    with col2:
        if st.session_state.show_cancelar_pedido_input:
            pedido_id_cancelar = st.text_input("ID do Pedido a Cancelar:", key="cancelar_pedido_id")
            if st.button("Confirmar Cancelamento", key="confirm_cancelar_pedido"):
                if pedido_id_cancelar:
                    success, result = api_post_streamlit(f"/pedidos/pedido/cancelar/{pedido_id_cancelar}")
                    if success:
                        message_placeholder.success(result.get("mensagem", "Pedido cancelado com sucesso."))
                    st.session_state.show_cancelar_pedido_input = False # Esconde o input após a ação
                else:
                    message_placeholder.error("Por favor, preencha o ID do pedido.")

    st.markdown("---") # Separador visual
    st.info("Para parar a aplicação, feche a aba do navegador ou pressione `Ctrl+C` no terminal onde o Streamlit está rodando.")

# --- Execução Principal ---
if __name__ == "__main__":
    main()

