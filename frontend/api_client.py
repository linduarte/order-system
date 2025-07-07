# api_client.py
import logging
import os

import httpx
from utils import read_token

# from api_client import decode_jwt

# URL da API e caminho do token
API_URL = "http://localhost:8000"
TOKEN_PATH = os.path.join(os.path.dirname(__file__), "token.txt")


# Função para realizar requisição HTTP
def api_request(method, endpoint, json_data=None):
    """
    Realiza uma requisição HTTP para o endpoint da API.

    :param method: O método HTTP (GET, POST, etc.)
    :param endpoint: O endpoint da API a ser chamado.
    :param json_data: Dados a serem enviados na requisição (se necessário).
    :return: A resposta da API ou None em caso de erro.
    """
    try:
        token = get_token()
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        url = f"{API_URL}{endpoint}"

        # Envia a requisição
        response = httpx.request(method, url, json=json_data, headers=headers)
        response.raise_for_status()  # Levanta um erro se a resposta for 4xx ou 5xx
        return response.json()  # Retorna o conteúdo JSON da resposta

    except httpx.HTTPStatusError as err:
        logging.error(f"Erro HTTP na requisição para {endpoint}: {err}")
        return None
    except Exception as e:
        logging.error(f"Erro ao realizar a requisição para {endpoint}: {e}")
        return None


# Função para obter o token do arquivo
def get_token():
    """
    Lê o token JWT do arquivo token.txt.

    :return: O token JWT ou None em caso de erro.
    """
    return read_token()


# Função para decodificar o JWT e obter o id do usuário
def decode_jwt(token):
    """
    Decodifica o token JWT e extrai o 'sub' (ID do usuário).

    :param token: O token JWT a ser decodificado.
    :return: O ID do usuário extraído do token ou None.
    """
    import base64
    import json

    try:
        payload = token.split(".")[1]
        padding = "=" * (-len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload + padding)
        return json.loads(decoded).get("sub")
    except Exception as e:
        logging.error(f"Erro ao decodificar o token JWT: {e}")
        return None
