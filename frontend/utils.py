# utils.py
import os
import logging


# Função auxiliar para ler o token do arquivo
def read_token():
    """
    Lê o token JWT do arquivo token.txt.

    :return: O token JWT ou None em caso de erro.
    """
    try:
        token_path = os.path.join(os.path.dirname(__file__), "access_token.txt")
        with open(token_path, "r") as file:
            return file.read().strip()
    except Exception as e:
        logging.error(f"Erro ao ler token: {e}")
        return None


# Função auxiliar para validar entradas (como campos obrigatórios)
def validar_entrada(valor, nome_campo):
    """
    Valida se o valor de um campo está vazio.

    :param valor: O valor do campo.
    :param nome_campo: O nome do campo, usado na mensagem de erro.
    :return: O valor se válido.
    :raise: ValueError se o campo estiver vazio.
    """
    if not valor:
        raise ValueError(f"O campo {nome_campo} não pode ser vazio.")
    return valor
