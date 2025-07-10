# 📦 Guia de Configuração e Execução do Projeto de Pedidos

Este `README.md` oferece um guia passo a passo para configurar e executar o sistema de pedidos, que consiste em um **backend (FastAPI/Uvicorn)** e um **frontend (Streamlit)**.

---

## 🗂️ Estrutura do Projeto

```
/seu_projeto/order-system/
├── backend/
│   ├── alembic/
│   │   ├── env.py
│   │   ├── README
│   │   ├── script.py.mako
│   │   └── versions/
│   │       ├── 0e8028701bbf_adicionar_admin_usuario.py
│   │       ├── 6d80a5480493_initial_migration.py
│   │       ├── 7ecabdec423f_remover_admin_usuario.py
│   │       └── 26bac5f0b4bf_adicionar_itens_no_pedido.py
│   ├── alembic.ini
│   ├── auth_routes.py
│   ├── banco.db
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── order_routes.py
│   └── schemas.py
├── frontend/
│   ├── dashboard.py
│   ├── dashboard_app.py
│   ├── logger.py
│   ├── main.py
│   ├── requests.py
│   ├── .streamlit/
│   │   └── config.toml
│   ├── tests/
│   │   ├── conftest.py
│   │   └── test_dashboard.py
│   └── token.txt
├── pyproject.toml
├── README.md
├── requirements.txt
├── test_login.py
└── uv.lock
```

---

## ✅ Pré-requisitos

- Python 3.8+
- Ferramenta recomendada: [`uv`](https://pypi.org/project/uv/) para gerenciamento de ambiente e dependências

### Instalar `uv`:

```bash
pip install uv
```

---

## ⚙️ Configuração do Backend

> O backend é construído com **FastAPI** e executado via **Uvicorn**.

### 1. Criar o arquivo `__init__.py` (Crucial!)

```bash
cd backend
touch __init__.py
cd ..
```

No PowerShell (Windows):

```powershell
New-Item -Path ".\__init__.py" -ItemType File
```

### 2. Instalar dependências do backend

```powershell
.\.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
```

### 3. Iniciar o servidor backend

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn backend.main:app --reload
```

Acesse: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 💻 Configuração do Frontend (Streamlit Dashboard)

> O frontend é um dashboard interativo construído com **Streamlit**.

### 1. Instalar dependências do frontend

```powershell
.\.venv\Scripts\Activate.ps1
uv pip install streamlit
```

### 2. (Opcional) Configurar tema do Streamlit

```toml
# frontend/.streamlit/config.toml

[theme]
primaryColor="#8B0000"
backgroundColor="#F0F2F6"
secondaryBackgroundColor="#FFFFFF"
textColor="#262730"
font="sans serif"
```

### 3. Iniciar o dashboard

```bash
streamlit run frontend/dashboard_app.py
```

Acesse: [http://localhost:8503](http://localhost:8503)

---

## 🔐 Processo de Login

1. Acesse o dashboard
2. Entre com um usuário válido (ex: `ana@test.com`)
3. Clique em **Entrar**
4. O token será salvo em `frontend/token.txt`
5. Para sair, clique em **Sair**

---

## 🧪 Testar Conexão com `test_login.py`

Edite com suas credenciais reais:

```python
EMAIL = "seu_email@exemplo.com"
SENHA = "sua_senha"
```

Execute com o ambiente virtual ativo:

```bash
uv run test_login.py
```

---

## 🧯 Solução de Problemas Comuns

| Erro                                                                 | Causa Provável                      | Solução |
|----------------------------------------------------------------------|-------------------------------------|---------|
| `WinError 10061`                                                     | Backend não está rodando            | Inicie o Uvicorn |
| `Could not import module "backend/main"`                             | Falta do `__init__.py`              | Crie o arquivo |
| `AttributeError: module 'streamlit' has no attribute 'experimental_rerun'` | API antiga do Streamlit     | Use `st.rerun()` |
| `Erro HTTP 500`, sem logs no backend                                 | Firewall/antivírus bloqueando       | Teste desativar temporariamente |
| `Erro HTTP 400: {"detail":"Usuário não encontrado..."}`              | Credenciais incorretas              | Verifique e-mail/senha |

---

## 🏁 Conclusão

Com este guia você será capaz de:

- Configurar backend com FastAPI/Uvicorn
- Executar frontend com Streamlit
- Diagnosticar e corrigir problemas com facilidade#Test
