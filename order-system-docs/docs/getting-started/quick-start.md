# Quick Start Guide

Get your Order Management System running in minutes! ⚡

## 🚀 Start the Application

### 1. Start Backend Server

```bash
# Navigate to project root
cd order-system

# Start FastAPI server
uvicorn backend.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### 2. Start Frontend Dashboard

```bash
# In a new terminal
streamlit run frontend/dashboard_app.py
```

You should see:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

## 🎯 First Steps

### 1. Access the Application

- **Frontend Dashboard**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **API Base URL**: http://localhost:8000

### 2. Create Your First User

Navigate to the registration page and create an account:

```json
{
  "email": "admin@example.com",
  "senha": "your-secure-password",
  "nome": "Admin User"
}
```

### 3. Login and Explore

1. **Login** with your credentials
2. **View Token Status** in the sidebar
3. **Create Orders** using the dashboard
4. **Add Items** to your orders
5. **Manage Order Status**

## 📊 Dashboard Overview

### Main Features

| Feature | Description |
|---------|-------------|
| **🔐 Authentication** | Secure login with JWT tokens |
| **📦 Order Management** | Create, view, and manage orders |
| **🛒 Item Management** | Add/remove items from orders |
| **👥 User Management** | Admin user controls |
| **📊 Status Tracking** | Real-time order status updates |

### Navigation

- **Home**: Overview and quick actions
- **Orders**: Create and manage orders
- **Items**: Add/remove order items
- **Profile**: User account settings
- **Admin**: Administrative functions (admin only)

## 🔧 Configuration

### Environment Variables

Key settings in your `.env` file:

```env
# Authentication
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120

# Database
DATABASE_URL=sqlite:///./orders.db

# API Settings
API_HOST=127.0.0.1
API_PORT=8000
```

### Default Settings

- **Access Token Expiry**: 2 hours
- **Database**: SQLite (local file)
- **API Port**: 8000
- **Frontend Port**: 8501

## 🎮 Try It Out!

### Example Workflow

1. **Create an order**:
   ```bash
   curl -X POST "http://localhost:8000/pedidos/pedido" \
   -H "Authorization: Bearer YOUR_TOKEN" \
   -H "Content-Type: application/json" \
   -d '{"usuario": 1}'
   ```

2. **Add items to order**:
   ```bash
   curl -X POST "http://localhost:8000/pedidos/pedido/1/item" \
   -H "Authorization: Bearer YOUR_TOKEN" \
   -H "Content-Type: application/json" \
   -d '{"nome": "Product 1", "quantidade": 2, "preco": 10.99}'
   ```

3. **View your orders** in the dashboard

## 🐛 Common Issues

!!! tip "Quick Fixes"
    - **Port in use**: Change port numbers in configuration
    - **Token expired**: Re-login to refresh tokens
    - **Database locked**: Restart the application

## 📚 What's Next?

- [API Documentation](../api/authentication.md)
- [Frontend Components](../frontend/dashboard.md)
- [Deployment Guide](../deployment/docker.md)

---

**Ready to dive deeper?** Check out the [API Documentation](../api/authentication.md)! 🚀