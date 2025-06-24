Guia de Configuração e Execução do Projeto de PedidosEste README.md oferece um guia passo a passo para configurar e executar o sistema de pedidos, que consiste em um backend (FastAPI/Uvicorn) e um frontend (Streamlit).Estrutura do ProjetoO projeto tem a seguinte estrutura de diretórios:/seu_projeto/order-system/
├── backend/
│   ├── alembic/                  # Gerenciamento de migrações de banco de dados (Alembic)
│   │   ├── env.py                # Ambiente de execução do Alembic para operações de migração
│   │   ├── README                # Documentação padrão do Alembic
│   │   ├── script.py.mako        # Template usado para gerar novos scripts de migração
│   │   └── versions/             # Diretório que armazena os scripts de migração do banco de dados (histórico de alterações)
│   │       ├── 0e8028701bbf_adicionar_admin_usuario.py
│   │       ├── 6d80a5480493_initial_migration.py
│   │       ├── 7ecabdec423f_remover_admin_usuario.py
│   │       └── 26bac5f0b4bf_adicionar_itens_no_pedido.py
│   ├── alembic.ini               # Arquivo de configuração principal do Alembic
│   ├── auth_routes.py            # Módulo contendo as rotas da API relacionadas à autenticação de usuários (login, registro, etc.)
│   ├── banco.db                  # Arquivo do banco de dados SQLite, onde os dados são persistidos
│   ├── config.py                 # Módulo para configurações globais do backend (ex: SECRET_KEY para JWT, algoritmos de hashing)
│   ├── database.py               # Módulo para configuração da conexão com o banco de dados e gerenciamento da sessão
│   ├── dependencies.py           # Funções e classes usadas para injeção de dependência no FastAPI (ex: verificação de token)
│   ├── __init__.py               # **Crucial: Arquivo vazio para tornar 'backend' um pacote Python e permitir importações relativas**
│   ├── main.py                   # Aplicação FastAPI principal, ponto de entrada para o servidor de backend
│   ├── models.py                 # Definições dos modelos de dados que mapeiam para as tabelas do banco de dados (usando SQLAlchemy ORM)
│   ├── order_routes.py           # Módulo contendo as rotas da API para o gerenciamento de pedidos (criação, listagem, atualização)
│   └── schemas.py                # Definições dos schemas de validação e serialização de dados para requisições e respostas da API (usando Pydantic)
├── frontend/
│   ├── dashboard.py              # Possível arquivo auxiliar ou versão anterior do dashboard (mencionado na sua estrutura, mas 'dashboard_app.py' é o principal agora)
│   ├── dashboard_app.py          # Aplicação Streamlit principal, contendo o dashboard interativo e a lógica de login
│   ├── logger.py                 # Configuração de logging para o aplicativo frontend
│   ├── main.py                   # Possível script de login original (Tkinter, etc. - não utilizado diretamente pelo Streamlit)
│   ├── requests.py               # Funções auxiliares para realizar requisições HTTP do frontend para o backend (se usado)
│   ├── .streamlit/               # Diretório para configurações específicas do Streamlit
│   │   └── config.toml           # Arquivo de configuração de tema customizado para o Streamlit
│   ├── tests/                    # Diretório para testes unitários ou de integração do frontend
│   │   ├── conftest.py
│   │   └── test_dashboard.py
│   └── token.txt                 # **Gerado e armazenado localmente após o login bem-sucedido na aplicação Streamlit**
├── pyproject.toml                # Arquivo de configuração do projeto (seguindo PEP 518/621), usado por `uv` e outras ferramentas modernas
├── README.md                     # Este arquivo de documentação do projeto
├── requirements.txt              # Lista tradicional de dependências Python para `pip install -r` (ou `uv pip install -r`)
├── test_login.py                 # Script Python independente para testar a rota de login da API diretamente, útil para depuração
└── uv.lock                       # Arquivo de bloqueio de dependências gerado por `uv`, garante instalações consistentes
Pré-requisitosCertifique-se de ter o Python 3.8+ instalado no seu sistema. É altamente recomendado usar uv para gerenciamento de ambientes e pacotes Python, devido à sua velocidade e eficiência.Instale uv (se ainda não tiver):pip install uv
Configuração do BackendO backend é construído com FastAPI e é executado via Uvicorn.1. Criar o arquivo __init__.py (Crucial!)Para que o Python e o Uvicorn reconheçam a pasta backend como um pacote Python e possam importar seus módulos internos (como main.py), ela deve conter um arquivo vazio chamado __init__.py.Navegue até o diretório backend do seu projeto:cd D:\reposground\work\order-system\backend
Crie o arquivo (se não existir):touch __init__.py
# Ou no Windows PowerShell:
# New-Item -Path ".\__init__.py" -ItemType File
Volte para o diretório raiz do projeto (order-system):cd ..
2. Instalar Dependências do BackendA partir do diretório raiz do seu projeto (D:\reposground\work\order-system), ative seu ambiente virtual e instale todas as dependências do projeto. É altamente recomendável usar o arquivo requirements.txt para garantir que todas as dependências corretas sejam instaladas:# Ative o ambiente virtual (se ainda não estiver ativo neste terminal)
.\.venv\Scripts\Activate.ps1

# Instale todas as dependências listadas no requirements.txt usando uv
uv pip install -r requirements.txt
3. Iniciar o Servidor Backend (API)Abra um primeiro terminal dedicado para o seu backend. A partir do diretório raiz do seu projeto (D:\reposground\work\order-system), execute:.\.venv\Scripts\Activate.ps1 # Ative o ambiente virtual neste terminal
uvicorn backend.main:app --reload
Deixe este terminal rodando e visível. Ele deve exibir mensagens indicando que o servidor Uvicorn está em execução, como:INFO: Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)Você pode verificar se a API está acessível no seu navegador abrindo http://localhost:8000/docs (se estiver usando FastAPI, esta rota exibirá a documentação interativa da sua API).Configuração do Frontend (Streamlit Dashboard)O frontend é um dashboard interativo construído com Streamlit.1. Instalar Dependências do FrontendAs dependências do frontend (incluindo Streamlit) já devem estar instaladas se você usou uv pip install -r requirements.txt no passo de instalação das dependências do backend. Caso contrário, ou para garantir que o Streamlit esteja disponível, abra um segundo terminal (novo e separado do primeiro). A partir do diretório raiz do seu projeto (D:\reposground\work\order-system), ative seu ambiente virtual e instale o Streamlit:.\.venv\Scripts\Activate.ps1 # Ative o ambiente virtual neste NOVO terminal
uv pip install streamlit
2. Configurar Tema do Streamlit (Opcional, mas Recomendado)Para customizar as cores e fontes do seu dashboard Streamlit, crie (ou edite) o arquivo config.toml dentro da pasta frontend/.streamlit/. Este arquivo é lido automaticamente pelo Streamlit para aplicar o tema.Crie a pasta .streamlit dentro de frontend (se ela ainda não existir).Crie o arquivo config.toml dentro de frontend/.streamlit/.# frontend/.streamlit/config.toml

[theme]
primaryColor="#8B0000"           # Cor principal para botões, sliders, etc. (Vermelho Escuro)
backgroundColor="#F0F2F6"        # Cor de fundo da página (Cinza Claro)
secondaryBackgroundColor="#FFFFFF" # Cor de fundo de containers e sidebars (Branco)
textColor="#262730"              # Cor do texto principal (Preto Quase Total)
font="sans serif"                # Tipo de fonte (pode ser "sans serif", "serif", "monospace")

# Você também pode adicionar o CSS para Nerd Font diretamente no dashboard_app.py conforme discutido anteriormente,
# para um controle mais granular sobre a tipografia.
3. Iniciar o Dashboard StreamlitNo segundo terminal (onde o ambiente virtual está ativo e o Streamlit foi instalado), e com o backend rodando e visível no primeiro terminal, execute:streamlit run frontend/dashboard_app.py
Isso deve abrir automaticamente uma nova aba no seu navegador padrão com o dashboard. Geralmente, ele estará acessível em http://localhost:8503.Processo de Login no DashboardAo abrir o dashboard Streamlit no seu navegador, você será redirecionado para a tela de Login.Insira as credenciais de um usuário válido que você tenha cadastrado no seu sistema de backend (por exemplo, ana@test.com e sua senha correspondente).Clique no botão "Entrar".Se o login for bem-sucedido, a tela de login será ocultada, e o dashboard principal de gerenciamento de pedidos será exibido. O token de autenticação será armazenado na sessão do Streamlit e salvo no arquivo frontend/token.txt para persistência entre as sessões.Para sair da sessão, clique no botão "Sair" que aparecerá no dashboard principal.Testando a Conexão da API (Ferramenta de Diagnóstico)Se você encontrar problemas de conexão ou erros 500 Internal Server Error no Streamlit novamente, pode usar o script test_login.py para diagnosticar a API diretamente, sem o Streamlit.Edite o arquivo test_login.py:Substitua os valores de EMAIL e SENHA pelas suas credenciais reais e válidas para o login.# test_login.py
import httpx
import json

API_URL = "http://localhost:8000"
EMAIL = "seu_email_real@exemplo.com" # <--- ATUALIZE AQUI COM SEU EMAIL DE TESTE
SENHA = "sua_senha_real"       # <--- ATUALIZE AQUI COM SUA SENHA DE TESTE

try:
    print(f"Tentando login em {API_URL}/auth/login com email: {EMAIL}")
    response = httpx.post(
        f"{API_URL}/auth/login",
        json={"email": EMAIL, "senha": SENHA},
        timeout=10 # Adiciona um tempo limite para a requisição
    )
    response.raise_for_status() # Levanta um erro para status 4xx/5xx
    print("Status Code:", response.status_code)
    print("Resposta JSON:", response.json())
except httpx.HTTPStatusError as err:
    print(f"Erro HTTP ({err.response.status_code}): {err.response.text}")
except httpx.RequestError as err:
    print(f"Erro de rede ao conectar à API: {err}")
except Exception as e:
    print(f"Erro inesperado: {e}")
Execute test_login.py:No segundo terminal (com ambiente virtual ativado, mas sem o Streamlit rodando), a partir do diretório raiz do projeto (D:\reposground\work\order-system):uv run test_login.py
Observe a saída neste terminal: Se você vir Status Code: 200 e o JSON com os tokens de acesso, isso confirma que sua API está funcionando corretamente para o login.Observe o terminal do Uvicorn (o primeiro): Se houver algum erro ou traceback detalhado, ele aparecerá aqui, indicando problemas internos na API.Solução de Problemas Comuns[WinError 10061] No connection could be made because the target machine actively refused it: Este erro indica que o backend (Uvicorn) não está rodando ou não está acessível na porta 8000.Verificação: Certifique-se de que o Uvicorn esteja ativo no primeiro terminal e exibindo a mensagem Uvicorn running on http://127.0.0.1:8000.ERROR: Error loading ASGI app. Could not import module "backend/main".: Este erro ocorre quando o Uvicorn não consegue encontrar ou importar o seu módulo main dentro da pasta backend.Verificação: Confirme que o arquivo vazio __init__.py existe dentro da pasta backend, e que você está executando o comando uvicorn a partir do diretório raiz do projeto (order-system).AttributeError: module 'streamlit' has no attribute 'experimental_rerun': Este erro indica que você está usando uma versão mais antiga da API do Streamlit.Solução: Substitua todas as ocorrências de st.experimental_rerun() por st.rerun() no seu dashboard_app.py. (Já corrigido nas últimas versões do código fornecidas).Erro HTTP (500): Internal Server Error no Streamlit, mas nenhum log no Uvicorn: Se o Streamlit relata um erro 500, mas o terminal do Uvicorn não mostra nenhuma requisição recebida ou traceback, isso frequentemente aponta para um problema de firewall ou antivírus bloqueando a comunicação entre o Streamlit e o Uvicorn, mesmo em localhost.Solução: Tente desativar temporariamente seu firewall ou software antivírus (com cautela, apenas para teste) para ver se o problema desaparece. Se resolver, adicione exceções para os processos do Python, Uvicorn e Streamlit no seu firewall.Erro HTTP (400): {"detail":"Usuário não encontrado ou credenciais inválidas"}: Este é um erro lógico da API, indicando que as credenciais (email/senha) fornecidas no login do Streamlit ou no test_login.py estão incorretas ou não correspondem a um usuário válido registrado no seu backend.Solução: Verifique as credenciais digitadas. Certifique-se de que correspondem exatamente a um usuário que você sabe que existe e está ativo no seu banco de dados de backend.Com este guia detalhado, você terá todas as informações necessárias para configurar, executar e solucionar problemas do seu projeto de pedidos.