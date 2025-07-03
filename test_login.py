import httpx
import json


API_URL = "http://localhost:8000"
EMAIL = "ana@test.com"  # SUBSTITUA PELO SEU EMAIL DE LOGIN REAL
SENHA = "ana123"  # SUBSTITUA PELA SUA SENHA REAL

try:
    print(f"Tentando login em {API_URL}/auth/login com email: {EMAIL}")
    response = httpx.post(
        f"{API_URL}/auth/login",
        json={"email": EMAIL, "senha": SENHA},
        timeout=10,  # Adiciona um timeout para não travar
    )
    response.raise_for_status()
    print("Status Code:", response.status_code)
    print("Resposta JSON:", response.json())
except httpx.HTTPStatusError as err:
    print(f"Erro HTTP ({err.response.status_code}): {err.response.text}")
except httpx.RequestError as err:
    print(f"Erro de rede ao conectar à API: {err}")
except Exception as e:
    print(f"Erro inesperado: {e}")
