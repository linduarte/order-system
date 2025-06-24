Sistema de Pedidos com FastAPI + Frontend Python
📦 Visão Geral
Este projeto é composto por duas camadas:

Backend: API REST com autenticação JWT e gestão de pedidos.

Frontend: Interface com Python + tkinter (via ttkbootstrap).

Inclui:

Logging

Tratamento de erros

Testes automatizados com cobertura

📁 Estrutura de Pastas
bash
Copy
Edit
project/
├── backend/
│   ├── auth_routes.py
│   ├── order_routes.py
│   └── ...
│
├── frontend/
│   ├── main.py          # Tela de login
│   ├── dashboard.py     # Interface com botões de ações
│   ├── requests.py      # Funções de requisição HTTP
│   ├── logger.py        # Logger do frontend
│   └── tests/
│       ├── test_dashboard.py
│       └── conftest.py
🚀 Instalação
Clonar o projeto:

bash
Copy
Edit
git clone https://github.com/seuusuario/sistema-pedidos.git
cd sistema-pedidos
Criar ambiente virtual:

bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows
Instalar dependências:

bash
Copy
Edit
pip install -r requirements.txt
Exemplo de requirements.txt:

nginx
Copy
Edit
fastapi
uvicorn
sqlalchemy
httpx
python-jose
passlib
ttkbootstrap
pytest
coverage
Iniciar o Backend:

bash
Copy
Edit
uvicorn backend.main:app --reload
Rodar o Frontend:

bash
Copy
Edit
cd frontend
python main.py
🧪 Testes
Executar testes com cobertura:

bash
Copy
Edit
cd frontend
pytest --cov=.
🗂️ Funcionalidades do Frontend
Login com email/senha e salva token

Dashboard com botões para:

Criar pedido

Listar pedidos

Adicionar/Remover itens

Finalizar ou Cancelar pedido

