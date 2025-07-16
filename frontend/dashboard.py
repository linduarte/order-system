import base64
import json
import os
import signal
from tkinter import messagebox, simpledialog

import httpx
import ttkbootstrap as tb
from ttkbootstrap.constants import DANGER, INFO, PRIMARY, SECONDARY, SUCCESS, WARNING

API_URL = "http://localhost:8000"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Shared path for the token file
TOKEN_PATH = os.path.join(os.path.dirname(__file__), "..", "access_token.txt")


signal.signal(signal.SIGINT, signal.SIG_IGN)  # Ignore Ctrl+C


def decode_jwt(token):
    try:
        payload_base64 = token.split(".")[1]
        # Preencher o base64 se necessário
        padding = 4 - len(payload_base64) % 4
        if padding != 4:
            payload_base64 += "=" * padding
        decoded = base64.urlsafe_b64decode(payload_base64)
        return json.loads(decoded)
    except Exception as e:
        print("[ERRO] Falha ao decodificar token:", e)
        return {}


def get_token():
    print(f"[DEBUG] Buscando token em: {TOKEN_PATH}")
    if not os.path.exists(TOKEN_PATH):
        messagebox.showerror("Erro", "Token não encontrado. Faça login novamente.")
        return None
    with open(TOKEN_PATH) as f:
        token = f.read().strip()
        print(f"[DEBUG] Token lido: {token[:40]}...")  # Mostra só o começo
        return token


def get_user_id():
    token = get_token()
    if not token:
        return None
    payload = decode_jwt(token)
    # pyrefly: ignore  # no-matching-overload
    return int(payload.get("sub")) if payload.get("sub") else None


def api_post(endpoint, json=None):
    token = get_token()
    if not token:
        return None
    headers = {"Authorization": f"Bearer {token}"}
    print(f"[DEBUG] POST para {API_URL}{endpoint} com json={json} e headers={headers}")
    try:
        response = httpx.post(f"{API_URL}{endpoint}", json=json, headers=headers)
        print(f"[DEBUG] Status: {response.status_code}, Resposta: {response.text}")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as err:
        print(f"[ERRO HTTP] {err.response.status_code}: {err.response.text}")
        messagebox.showerror("Erro API", err.response.text)
    except Exception as e:
        print(f"[ERRO GERAL] {e}")
        messagebox.showerror("Erro", str(e))


def api_get(endpoint):
    token = get_token()
    if not token:
        return None
    headers = {"Authorization": f"Bearer {token}"}
    print(f"[DEBUG] GET para {API_URL}{endpoint} com headers={headers}")
    try:
        response = httpx.get(f"{API_URL}{endpoint}", headers=headers)
        print(f"[DEBUG] Status: {response.status_code}, Resposta: {response.text}")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as err:
        print(f"[ERRO HTTP] {err.response.status_code}: {err.response.text}")
        messagebox.showerror("Erro API", err.response.text)
    except Exception as e:
        print("[ERRO EXCEÇÃO]", str(e))
        messagebox.showerror("Erro", str(e))


def api_delete(endpoint):
    token = get_token()
    if not token:
        return None
    headers = {"Authorization": f"Bearer {token}"}
    print(f"[DEBUG] DELETE para {API_URL}{endpoint} com headers={headers}")
    try:
        response = httpx.delete(f"{API_URL}{endpoint}", headers=headers)
        print(f"[DEBUG] Status: {response.status_code}, Resposta: {response.text}")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as err:
        print(f"[ERRO HTTP] {err.response.status_code}: {err.response.text}")
        messagebox.showerror("Erro API", err.response.text)
    except Exception as e:
        print("[ERRO EXCEÇÃO]", str(e))
        messagebox.showerror("Erro", str(e))


def run():
    print("[DEBUG] Dashboard iniciado.")
    app = tb.Window(themename="superhero")
    app.title("Dashboard de Pedidos")
    app.geometry("400x400")

    def criar_pedido():
        try:
            id_usuario_str = simpledialog.askstring(
                "Criar Pedido", "Digite o ID do usuário:"
            )
            if not id_usuario_str or not id_usuario_str.isdigit():
                messagebox.showerror("Erro", "ID do usuário inválido.")
                return

            id_usuario = int(id_usuario_str)
            resultado = api_post("/pedidos/pedido", json={"id_usuario": id_usuario})

            if resultado:
                msg = resultado.get("mensagem", "Pedido criado com sucesso.")
                messagebox.showinfo("Sucesso", msg)

        except Exception as e:
            print(f"[ERRO] Exception in criar_pedido: {e}")
            messagebox.showerror("Erro", str(e))

    def listar_pedidos():
        id_usuario = get_user_id()  # Get the user ID from the token
        if not id_usuario:
            messagebox.showerror("Erro", "Usuário não encontrado.")
            return

        # resultado = api_get(f"/pedidos/usuario_id={id_usuario}")  # Pass
        resultado = api_get("/pedidos/listar/pedidos-usuario")
        if resultado:
            pedidos = "\n".join(
                [f"ID {p['id']} - Status: {p['status']}" for p in resultado]
            )
            messagebox.showinfo("Pedidos", pedidos)
        else:
            messagebox.showinfo(
                "Pedidos", "Nenhum pedido encontrado."
            )  # Handle empty result

    def adicionar_item():
        id_pedido = simpledialog.askstring("Adicionar Item", "ID do Pedido:")
        quantidade = simpledialog.askinteger("Adicionar Item", "Quantidade:")
        sabor = simpledialog.askstring("Adicionar Item", "Sabor:")
        tamanho = simpledialog.askstring(
            "Adicionar Item", "Tamanho (Pequeno, Médio, Grande):"
        )
        preco_unitario = simpledialog.askfloat("Adicionar Item", "Preço Unitário:")

        if id_pedido and quantidade and sabor and tamanho and preco_unitario:
            data = {
                "quantidade": quantidade,
                "sabor": sabor,
                "tamanho": tamanho,
                "preco_unitario": preco_unitario,
            }
        try:
            result = api_post(f"/pedidos/pedido/adicionar-item/{id_pedido}", json=data)
            if result:
                messagebox.showinfo("Sucesso", "Item adicionado com sucesso ao pedido.")
        except Exception as e:
            print(f"[ERRO] Erro ao adicionar item: {e}")
            messagebox.showerror("Erro", "Erro ao adicionar item.")

    def remover_item():
        id_item_pedido = simpledialog.askstring("Remover Item", "ID do Item do Pedido:")
        if id_item_pedido:
            try:
                # Proceed with removing the item
                result = api_delete(f"/pedidos/pedido/remover-item/{id_item_pedido}")
                if result:
                    messagebox.showinfo(
                        "Sucesso", "Item removido com sucesso do pedido."
                    )
                else:
                    messagebox.showerror(
                        "Erro",
                        "Erro ao remover item. Verifique se o ID do item está correto.",
                    )
            except Exception as e:
                print(f"[ERRO] Erro ao remover item: {e}")
                messagebox.showerror("Erro", "Erro ao remover item.")

    def finalizar_pedido():
        id_pedido = simpledialog.askstring("Finalizar Pedido", "ID do Pedido:")
        if id_pedido:
            api_post(f"/pedidos/pedido/finalizar/{id_pedido}")

    def cancelar_pedido():
        id_pedido = simpledialog.askstring("Cancelar Pedido", "ID do Pedido:")
        if id_pedido:
            api_post(f"/pedidos/pedido/cancelar/{id_pedido}")

    def close_app():
        print("[INFO] Closing application...")
        app.destroy()  # Gracefully close the Tkinter window

    # pyrefly: ignore  # unexpected-keyword
    tb.Button(app, text="Criar Pedido", command=criar_pedido, bootstyle=SUCCESS).pack(
        pady=10
    )
    tb.Button(
        # pyrefly: ignore  # unexpected-keyword
        app, text="Listar Meus Pedidos", command=listar_pedidos, bootstyle=PRIMARY
    ).pack(pady=10)
    # pyrefly: ignore  # unexpected-keyword
    tb.Button(app, text="Adicionar Item", command=adicionar_item, bootstyle=INFO).pack(
        pady=10
    )
    # pyrefly: ignore  # unexpected-keyword
    tb.Button(app, text="Remover Item", command=remover_item, bootstyle=WARNING).pack(
        pady=10
    )
    tb.Button(
        # pyrefly: ignore  # unexpected-keyword
        app, text="Finalizar Pedido", command=finalizar_pedido, bootstyle=SECONDARY
    ).pack(pady=10)
    tb.Button(
        # pyrefly: ignore  # unexpected-keyword
        app, text="Cancelar Pedido", command=cancelar_pedido, bootstyle=DANGER
    ).pack(pady=10)
    # pyrefly: ignore  # unexpected-keyword
    tb.Button(app, text="Fechar", command=close_app, bootstyle="danger").pack(
        pady=10
    )  # Add Close button

    try:
        app.mainloop()
    except KeyboardInterrupt:
        print("[INFO] Application interrupted by user.")
        exit(0)  # Ensure the program exits cleanly
    except Exception as e:
        print(f"[ERRO] Exception in mainloop: {e}")


if __name__ == "__main__":
    run()
