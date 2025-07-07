# Installation Guide

This guide will help you set up the Order Management System using **UV** - the ultra-fast Python package manager.

## ⚡ **Why UV?**

We use **[UV](https://github.com/astral-sh/uv)** - the revolutionary Python package manager by **Astral**:

- 🚀 **10-100x faster** than pip
- 🔒 **Enhanced security** with dependency resolution
- 🛠️ **Modern workflows** - replaces pip + virtualenv
- 🎯 **Simple commands** - streamlined developer experience
- 🔗 **Built in Rust** - maximum performance

---

## 📋 **Prerequisites**

- **Python 3.8+** - [Download Python](https://python.org/downloads/)
- **Git** - [Download Git](https://git-scm.com/downloads/)
- **UV** - Ultra-fast Python package manager

---

## ⚡ **Install UV**

=== "Windows"
    ```bash
    # Install via pip (one-time setup)
    pip install uv
    
    # Or via PowerShell (recommended)
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

=== "macOS/Linux"
    ```bash
    # Install via curl
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Or via pip
    pip install uv
    ```

=== "Verify Installation"
    ```bash
    uv --version
    # Should show: uv x.x.x
    ```

---

## 🚀 **Quick Installation with UV**

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/order-system.git
cd order-system

# Initialize UV project (creates virtual environment automatically)
uv init

# Sync all dependencies (backend + frontend)
uv sync
```

### 2. Install Project Dependencies

```bash
# Install backend dependencies
cd backend
uv add fastapi uvicorn sqlalchemy python-jose[cryptography] passlib[bcrypt] python-multipart

# Install frontend dependencies  
cd ../frontend
uv add streamlit httpx python-dotenv

# Install development dependencies
uv add --dev pytest mkdocs mkdocs-material bandit black ruff
```

### 3. Environment Setup

```bash
# Create .env file in backend directory
echo "SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120
DATABASE_URL=sqlite:///./orders.db" > backend/.env
```

---

## 🎯 **UV vs Traditional Approach**

| Task | Traditional | With UV | Speed Improvement |
|------|-------------|---------|-------------------|
| **Create venv** | `python -m venv venv` | `uv init` | 🚀 **100x faster** |
| **Activate venv** | `source venv/bin/activate` | *automatic* | ⚡ **Always active** |
| **Install packages** | `pip install package` | `uv add package` | 🏃 **10-100x faster** |
| **Install from file** | `pip install -r requirements.txt` | `uv sync` | 🔥 **50x faster** |
| **Dependency resolution** | *basic* | *advanced* | 🛡️ **Much safer** |

---

## ✅ **Verify Installation**

Test your setup with UV:

```bash
# Run backend with UV
cd backend
uv run uvicorn main:app --reload

# Run frontend with UV (in another terminal)
cd frontend  
uv run streamlit run dashboard_app.py
```

---

## 🔧 **UV Project Structure**

After UV initialization, your project will have:

```
order-system/
├── pyproject.toml          ← UV project configuration
├── uv.lock                 ← Dependency lock file (auto-generated)
├── .venv/                  ← Virtual environment (auto-created)
├── backend/
│   ├── main.py
│   ├── requirements.txt    ← Optional (for compatibility)
│   └── .env
├── frontend/
│   ├── dashboard_app.py
│   └── requirements.txt    ← Optional (for compatibility)
└── ...
```

---

## 🚀 **UV Commands Cheat Sheet**

```bash
# Project initialization
uv init                     # Initialize new project
uv sync                     # Install all dependencies

# Package management  
uv add package              # Add package to project
uv add --dev package        # Add development dependency
uv remove package           # Remove package
uv list                     # List installed packages

# Running commands
uv run python script.py     # Run Python script
uv run pytest              # Run tests
uv run --                   # Run arbitrary command

# Virtual environment
uv venv                     # Create virtual environment
uv pip install package     # Use uv's pip implementation
```

---

## 💡 **Modern Python Development**

### UV Benefits for This Project

✅ **Lightning Fast** - Dependencies install in seconds  
✅ **Automatic venv** - No manual virtual environment management  
✅ **Dependency Safety** - Advanced conflict resolution  
✅ **Modern Workflow** - Single tool for all package operations  
✅ **Cross-platform** - Works identically on Windows/Mac/Linux  

### Integration with Development Tools

```bash
# Code formatting with UV
uv run black .
uv run ruff check .

# Testing with UV
uv run pytest backend/tests/
uv run pytest frontend/tests/

# Documentation with UV
uv run mkdocs serve
```

---

## 🐳 **Docker with UV** (Optional)

Update your Dockerfile to use UV:

```dockerfile
FROM python:3.11-slim

# Install UV
RUN pip install uv

WORKDIR /app

# Copy UV configuration
COPY pyproject.toml uv.lock ./

# Install dependencies with UV
RUN uv sync --frozen

# Copy application code
COPY . .

# Run with UV
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🆚 **Legacy Installation** (pip/virtualenv)

<details>
<summary>Click to see traditional installation method</summary>

```bash
# Old way (still works but slower)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

</details>

---

!!! tip "UV Recommendation"
    **UV is the future of Python package management!** It's developed by the same team behind **Ruff** (the ultra-fast Python linter) and represents the next generation of Python tooling.

---

**Ready to experience the speed?** Install UV and feel the difference! ⚡🚀