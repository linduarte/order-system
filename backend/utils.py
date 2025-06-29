"""Utility functions for the FastAPI application.

This module provides helper functions, such as saving tokens to files.
"""

import logging
import os


def save_token_to_file(
    token: str,
    filename: str = os.path.join(os.path.dirname(__file__), "..", "access_token.txt"),
):
    """
    Saves a given token string to a text file.

    Args:
        token (str): The access token to be saved.
        filename (str): The name of the file to save the token to.
    """
    try:
        with open(filename, "w") as file:
            file.write(token)
        logging.info(f"Token salvo com sucesso em '{filename}'")
    except IOError as e:
        logging.error(f"Erro ao salvar o token no arquivo '{filename}' : {e}")
