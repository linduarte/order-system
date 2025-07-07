import os
from tkinter import messagebox

import httpx
import ttkbootstrap as tb
from dashboard import run  # Certo!
from ttkbootstrap.constants import SUCCESS

# Caminho absoluto para salvar o token
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH = os.path.join(BASE_DIR, "token.txt")
API_URL = "http://localhost:8000"


class LoginApp(tb.Window):
    def __init__(self):
        super().__init__(themename="superhero")
        self.title("Login - Sistema de Pedidos")
        self.geometry("400x250")
        self.resizable(False, False)
        self.create_widgets()

    def create_widgets(self):
        tb.Label(self, text="Email:").pack(pady=5)
        self.entry_email = tb.Entry(self, width=30)
        self.entry_email.pack(pady=5)

        tb.Label(self, text="Senha:").pack(pady=5)
        self.entry_senha = tb.Entry(self, show="*", width=30)
        self.entry_senha.pack(pady=5)

        tb.Button(
            self, text="Entrar", bootstyle=SUCCESS, command=self.fazer_login
        ).pack(pady=15)

    def fazer_login(self):
        email = self.entry_email.get().strip()
        senha = self.entry_senha.get().strip()

        if not email or not senha:
            messagebox.showwarning("Campos obrigatórios", "Preencha email e senha.")
            return

        print("[DEBUG] Tentando login com:", email)

        try:
            token = self.autenticar(email, senha)
            if token:
                self.salvar_token(token)
                messagebox.showinfo("Sucesso", "Login realizado com sucesso!")

                self.withdraw()  # Oculta a janela principal
                print("[DEBUG] Chamando dashboard...")
                self.after(200, run)

        except httpx.HTTPStatusError as err:
            detalhe = err.response.json().get("detail", "Erro desconhecido")
            print("[DEBUG] Erro HTTP no login:", detalhe)
            messagebox.showerror("Erro no login", f"Detalhe: {detalhe}")
        except Exception as e:
            print("[DEBUG] Erro inesperado:", str(e))
            messagebox.showerror("Erro", f"Erro inesperado: {e}")

    def autenticar(self, email: str, senha: str) -> str | None:
        response = httpx.post(
            f"{API_URL}/auth/login", json={"email": email, "senha": senha}
        )
        response.raise_for_status()
        return response.json().get("access_token")

    def salvar_token(self, token: str):
        with open(TOKEN_PATH, "w") as f:
            f.write(token)
        print("[DEBUG] Token salvo com sucesso.")


if __name__ == "__main__":
    print("[DEBUG] Iniciando LoginApp...")
    app = LoginApp()
    app.mainloop()
