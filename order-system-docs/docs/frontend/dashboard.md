# Dashboard Guide

Complete guide to using the Streamlit dashboard for order management.

## 🎨 Dashboard Overview

The Streamlit dashboard provides an intuitive interface for managing orders, items, and user accounts.

## 🔐 Authentication Flow

### Login Process

1. **Access the Dashboard**
   ```
   http://localhost:8501
   ```

2. **Navigate to Login**
   - Click "Login" in the sidebar
   - Enter your credentials
   - Click "Entrar"

3. **Token Management**
   - Tokens are automatically saved
   - Status shown in sidebar
   - Auto-refresh when needed

## 📦 Order Management

### Creating Orders

1. **Navigate to "Criar Pedido"**
2. **System automatically**:
   - Validates your authentication
   - Extracts user ID from token
   - Creates order with PENDENTE status
3. **Success message** shows order ID

### Viewing Orders

**Order List Features:**
- ✅ All your orders displayed
- 📊 Order status indicators
- 💰 Total value calculation
- 📅 Creation date/time
- 🔍 Quick order details

## 🛒 Item Management

### Adding Items to Orders

1. **Select an Order** (must be PENDENTE)
2. **Fill Item Information**:
   - **Nome**: Product name
   - **Quantidade**: Number of items
   - **Preço**: Unit price
3. **Click "Adicionar Item"**

### Removing Items

1. **View Order Items**
2. **Click "Remover" button** next to item
3. **Confirmation dialog**
4. **Automatic recalculation** of order total

## 🎛️ Sidebar Features

### Token Status Panel

```
🔐 Token Status
Access Token: 🟢 Recent
Created: 14:30:25
Refresh Token: 🟢 Recent
Created: 14:30:25
```

### Quick Actions

- 🔄 **Refresh Tokens** - Manual token refresh
- 🚪 **Logout** - Clear tokens and logout
- ℹ️ **System Info** - View system status

---

**Ready to start using it?** Your dashboard is fully functional! 🚀