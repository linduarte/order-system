# Docker Deployment

Deploy your Order Management System using Docker for consistent, scalable, and portable deployment.

## 🐳 Docker Overview

Docker containerization provides:
- **Consistent Environment** - Same setup everywhere
- **Easy Deployment** - One command deployment
- **Scalability** - Easy to scale services
- **Isolation** - Services run independently

### Architecture

```mermaid
graph TB
    A[🌐 Load Balancer] --> B[📦 Frontend Container]
    A --> C[🚀 Backend Container]
    C --> D[🗄️ Database Container]
    C --> E[📁 Volume - Tokens]
    C --> F[📁 Volume - Database]
    
    style A fill:#e3f2fd
    style B fill:#e8f5e9
    style C fill:#fff3e0
    style D fill:#fce4ec
    style E fill:#f3e5f5
    style F fill:#f3e5f5
```

## 📁 Docker Files

### 1. Backend Dockerfile

**`backend/Dockerfile`:**
```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p tokens logs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Frontend Dockerfile

**`frontend/Dockerfile`:**
```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run application
CMD ["streamlit", "run", "dashboard_app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
```

### 3. Docker Compose

**`docker-compose.yml`:**
```yaml
version: '3.8'

services:
  # Backend Service
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: order-backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./data/orders.db
      - SECRET_KEY=${SECRET_KEY}
      - ALGORITHM=HS256
      - ACCESS_TOKEN_EXPIRE_MINUTES=120
    volumes:
      - ./data:/app/data
      - ./backend/tokens:/app/tokens
      - ./logs:/app/logs
    networks:
      - order-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Frontend Service
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: order-frontend
    ports:
      - "8501:8501"
    environment:
      - API_BASE_URL=http://backend:8000
    depends_on:
      - backend
    networks:
      - order-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Database Service (PostgreSQL for production)
  database:
    image: postgres:15-alpine
    container_name: order-database
    environment:
      - POSTGRES_DB=orders
      - POSTGRES_USER=orderuser
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - order-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U orderuser -d orders"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Redis for caching (optional)
  redis:
    image: redis:7-alpine
    container_name: order-redis
    ports:
      - "6379:6379"
    networks:
      - order-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: order-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    networks:
      - order-network
    restart: unless-stopped

networks:
  order-network:
    driver: bridge

volumes:
  postgres_data:
    driver: local
```

### 4. Environment Configuration

**`.env`:**
```env
# Application Settings
SECRET_KEY=your-super-secret-key-here-change-in-production
DB_PASSWORD=secure-database-password
API_BASE_URL=http://localhost:8000

# Database Configuration
DATABASE_URL=postgresql://orderuser:${DB_PASSWORD}@database:5432/orders

# Production Settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info

# SSL Configuration
SSL_CERT_PATH=/etc/nginx/ssl/cert.pem
SSL_KEY_PATH=/etc/nginx/ssl/key.pem
```

## 🚀 Deployment Steps

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/yourusername/order-system.git
cd order-system

# 2. Create environment file
cp .env.example .env
# Edit .env with your configuration

# 3. Build and start services
docker-compose up --build -d

# 4. Check service status
docker-compose ps

# 5. View logs
docker-compose logs -f
```

### Production Deployment

=== "Development"
    ```bash
    # Development environment
    docker-compose -f docker-compose.dev.yml up --build
    
    # Services available at:
    # Frontend: http://localhost:8501
    # Backend: http://localhost:8000
    # Database: localhost:5432
    ```

=== "Production"
    ```bash
    # Production environment
    docker-compose -f docker-compose.prod.yml up -d --build
    
    # Services available at:
    # Frontend: https://yourdomain.com
    # Backend: https://yourdomain.com/api
    # Admin: https://yourdomain.com/admin
    ```

=== "Staging"
    ```bash
    # Staging environment
    docker-compose -f docker-compose.staging.yml up -d
    
    # Services available at:
    # Frontend: https://staging.yourdomain.com
    # Backend: https://staging.yourdomain.com/api
    ```

## 🔧 Service Management

### Container Operations

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart specific service
docker-compose restart backend

# View service logs
docker-compose logs -f backend

# Execute command in container
docker-compose exec backend bash

# Scale services
docker-compose up -d --scale backend=3
```

### Database Management

```bash
# Database backup
docker-compose exec database pg_dump -U orderuser orders > backup.sql

# Database restore
docker-compose exec -T database psql -U orderuser orders < backup.sql

# Database migration
docker-compose exec backend alembic upgrade head

# Access database shell
docker-compose exec database psql -U orderuser -d orders
```

### Monitoring Commands

```bash
# Check container health
docker-compose ps

# Monitor resource usage
docker stats

# View container logs
docker-compose logs --tail=100 -f

# Inspect container
docker-compose exec backend env
```

## 🔒 Security Configuration

### SSL/TLS Setup

**`nginx/nginx.conf`:**
```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }
    
    upstream frontend {
        server frontend:8501;
    }
    
    # HTTP to HTTPS redirect
    server {
        listen 80;
        server_name yourdomain.com;
        return 301 https://$server_name$request_uri;
    }
    
    # HTTPS configuration
    server {
        listen 443 ssl http2;
        server_name yourdomain.com;
        
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        
        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        
        # Frontend proxy
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Backend API proxy
        location /api/ {
            proxy_pass http://backend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### Security Best Practices

!!! warning "Production Security"
    - Change default passwords
    - Use strong SECRET_KEY
    - Enable SSL/TLS
    - Configure firewall rules
    - Regular security updates
    - Monitor access logs

## 📊 Monitoring & Logging

### Health Checks

```bash
# Check all services
curl -f http://localhost:8000/health
curl -f http://localhost:8501/_stcore/health

# Database health
docker-compose exec database pg_isready -U orderuser

# Redis health
docker-compose exec redis redis-cli ping
```

### Log Management

```bash
# View all logs
docker-compose logs

# Follow specific service logs
docker-compose logs -f backend

# Log rotation configuration
docker-compose logs --tail=1000 > logs/app.log
```

### Monitoring Stack (Optional)

Add monitoring with Prometheus and Grafana:

```yaml
# Additional services in docker-compose.yml
prometheus:
  image: prom/prometheus
  container_name: order-prometheus
  ports:
    - "9090:9090"
  volumes:
    - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
  networks:
    - order-network

grafana:
  image: grafana/grafana
  container_name: order-grafana
  ports:
    - "3000:3000"
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=admin
  networks:
    - order-network
```

## 🚨 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **Port conflicts** | Change ports in docker-compose.yml |
| **Database connection** | Check DATABASE_URL format |
| **SSL certificates** | Verify certificate paths |
| **Memory issues** | Increase Docker memory limits |

### Debugging Commands

```bash
# Check container status
docker-compose ps

# Inspect container configuration
docker-compose config

# View container resource usage
docker stats

# Network troubleshooting
docker network ls
docker network inspect order-system_order-network
```

## 🔄 Updates & Maintenance

### Application Updates

```bash
# 1. Pull latest changes
git pull origin main

# 2. Rebuild containers
docker-compose build --no-cache

# 3. Update services
docker-compose up -d

# 4. Verify deployment
docker-compose ps
docker-compose logs -f
```

### Database Migrations

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"
```

---

**Next:** [Production Deployment](production.md) 🏭