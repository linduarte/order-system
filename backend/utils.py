import json
import os
from datetime import datetime
import logging


def save_token_to_file(
    access_token: str, refresh_token: str = None, filename: str = "access_token.txt"
):
    """
    Salva os tokens de acesso e refresh em arquivos JSON com timestamp.

    Args:
        access_token (str): O token de acesso JWT
        refresh_token (str, optional): O token de refresh JWT
        filename (str): Nome base do arquivo (usado para compatibilidade)
    """
    try:
        timestamp = datetime.now().isoformat()

        # Define paths
        base_dir = os.path.dirname(__file__)
        access_token_path = os.path.join(base_dir, "..", "access_token.txt")
        refresh_token_path = os.path.join(base_dir, "..", "refresh_token.txt")

        # Save access token with metadata
        access_data = {
            "token": access_token,
            "created_at": timestamp,
            "type": "access_token",
        }
        with open(access_token_path, "w") as f:
            json.dump(access_data, f, indent=2)

        # Save refresh token if provided
        if refresh_token:
            refresh_data = {
                "token": refresh_token,
                "created_at": timestamp,
                "type": "refresh_token",
            }
            with open(refresh_token_path, "w") as f:
                json.dump(refresh_data, f, indent=2)

            logging.info(
                f"Access token e refresh token salvos com sucesso em {timestamp}"
            )
        else:
            logging.info(f"Access token salvo com sucesso em {timestamp}")

    except IOError as e:
        logging.error(f"Erro ao salvar tokens: {e}")
    except Exception as e:
        logging.error(f"Erro inesperado ao salvar tokens: {e}")
