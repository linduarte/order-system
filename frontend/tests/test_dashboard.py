import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add parent directory to sys.path using pathlib
sys.path.insert(0, str(Path(__file__).parent.parent))
# pyrefly: ignore  # missing-module-attribute
from frontend import http_requests as req


@patch("frontend.requests.carregar_token", return_value="fake-token")
@patch("httpx.Client.request")
def test_requisicao_autenticada_sucesso(mock_request, mock_token):
    mock_request.return_value.status_code = 200
    mock_request.return_value.json.return_value = {"msg": "ok"}

    resp = req.requisicao_autenticada("GET", "/pedidos/listar/pedidos-usuario")
    assert resp["msg"] == "ok"


@patch("httpx.Client.request")
def test_requisicao_publica_sucesso(mock_request):
    mock_request.return_value.status_code = 200
    mock_request.return_value.json.return_value = {"versao": "1.0"}

    resp = req.requisicao_publica("GET", "/auth/")
    assert resp["versao"] == "1.0"


@patch("frontend.requests.carregar_token", side_effect=FileNotFoundError)
def test_token_nao_encontrado(mock_token):
    with pytest.raises(Exception, match="Token n\\u00e3o encontrado"):
        req.requisicao_autenticada("GET", "/pedidos/listar")
