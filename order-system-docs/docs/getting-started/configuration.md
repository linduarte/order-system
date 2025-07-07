# Configuration

Configure your Order Management System for optimal performance.

## ⚙️ Environment Variables

### Backend Configuration

Create `.env` file in the backend directory:

```env
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120
DATABASE_URL=sqlite:///./orders.db
```

### Frontend Configuration

The frontend automatically connects to:
- Backend API: `http://localhost:8000`
- Dashboard: `http://localhost:8501`

## 🔧 Advanced Settings

### Database Settings
- Connection pooling
- Query optimization
- Backup configuration

### Security Settings
- JWT configuration
- CORS settings
- Rate limiting

---

**Your system is now properly configured!** 🎯