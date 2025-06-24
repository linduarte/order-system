import ttkbootstrap as tb
from ttkbootstrap.constants import SUCCESS
from tkinter import messagebox
import httpx
from dashboard import run  # Corrigido aqui!
import os

# Caminho absoluto do token
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH = os.path.join(BASE_DIR, "token.txt")
API_URL = "http://localhost:8000"


class LoginApp(tb.Window):
    def __init__(self):
        super().__init__(themename="superhero")
        self.title("Login - Sistema de Pedidos")
        self.geometry("400x250")
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
        email = self.entry_email.get()
        senha = self.entry_senha.get()

        print("[DEBUG] Tentando login com:", email)  # DEBUG

        try:
            response = httpx.post(
                f"{API_URL}/auth/login", json={"email": email, "senha": senha}
            )
            response.raise_for_status()
            token = response.json()["access_token"]

            print("[DEBUG] Login bem-sucedido, token recebido")

            with open(TOKEN_PATH, "w") as f:
                f.write(token)

            messagebox.showinfo("Sucesso", "Login realizado com sucesso!")

            self.withdraw()  # Oculta a janela de login sem destruí-la
            print("[DEBUG] Chamando dashboard...")
            self.after(200, run)

        except httpx.HTTPStatusError as err:
            print("[DEBUG] Erro HTTP no login:", err.response.text)
            messagebox.showerror("Erro", f"Falha no login: {err.response.text}")
        except Exception as e:
            print("[DEBUG] Erro inesperado no login:", str(e))
            messagebox.showerror("Erro", str(e))


if __name__ == "__main__":
    print("[DEBUG] Iniciando LoginApp...")
    app = LoginApp()
    app.mainloop()
