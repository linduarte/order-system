# Production Deployment

Deploy your Order Management System to production with high availability, security, and performance.

## 🏭 Production Architecture

### High-Level Overview

```mermaid
graph TB
    A[🌐 Internet] --> B[☁️ Cloud Load Balancer]
    B --> C[🔒 WAF/CDN]
    C --> D[🚀 App Server 1]
    C --> E[🚀 App Server 2]
    C --> F[🚀 App Server 3]
    D --> G[🗄️ Primary Database]
    E --> G
    F --> G
    G --> H[🔄 Database Replica]
    D --> I[⚡ Redis Cache]
    E --> I
    F --> I
    
    style A fill:#e3f2fd
    style B fill:#e8f5e9
    style C fill:#fff3e0
    style D fill:#fce4ec
    style E fill:#fce4ec
    style F fill:#fce4ec
    style G fill:#f3e5f5
    style H fill:#f3e5f5
    style I fill:#ffebee
```

## ☁️ Cloud Deployment Options

### AWS Deployment

=== "EC2 + RDS"
    ```yaml
    # Infrastructure as Code (Terraform)
    resource "aws_instance" "order_app" {
      ami           = "ami-0c55b159cbfafe1d0"
      instance_type = "t3.medium"
      
      user_data = <<-EOF
        #!/bin/bash
        # Install Docker
        yum update -y
        yum install -y docker
        systemctl start docker
        systemctl enable docker
        
        # Install Docker Compose
        curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
        
        # Deploy application
        git clone https://github.com/yourusername/order-system.git
        cd order-system
        docker-compose -f docker-compose.prod.yml up -d
      EOF
      
      tags = {
        Name = "OrderManagementSystem"
      }
    }
    
    resource "aws_db_instance" "order_db" {
      identifier = "order-database"
      engine     = "postgres"
      engine_version = "15.3"
      instance_class = "db.t3.micro"
      allocated_storage = 20
      
      db_name  = "orders"
      username = "orderuser"
      password = var.db_password
      
      vpc_security_group_ids = [aws_security_group.db.id]
      
      backup_retention_period = 7
      backup_window = "03:00-04:00"
      maintenance_window = "sun:04:00-sun:05:00"
      
      tags = {
        Name = "OrderDatabase"
      }
    }
    ```

=== "ECS Fargate"
    ```yaml
    # ECS Task Definition
    version: '3'
    services:
      order-backend:
        image: your-registry/order-backend:latest
        cpu: 512
        memory: 1024
        environment:
          - DATABASE_URL=${DATABASE_URL}
          - SECRET_KEY=${SECRET_KEY}
        logging:
          driver: awslogs
          options:
            awslogs-group: /ecs/order-system
            awslogs-region: us-east-1
            awslogs-stream-prefix: backend
      
      order-frontend:
        image: your-registry/order-frontend:latest
        cpu: 256
        memory: 512
        ports:
          - "8501:8501"
        depends_on:
          - order-backend
        logging:
          driver: awslogs
          options:
            awslogs-group: /ecs/order-system
            awslogs-region: us-east-1
            awslogs-stream-prefix: frontend
    ```

=== "Kubernetes"
    ```yaml
    # Kubernetes Deployment
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: order-backend
    spec:
      replicas: 3
      selector:
        matchLabels:
          app: order-backend
      template:
        metadata:
          labels:
            app: order-backend
        spec:
          containers:
          - name: backend
            image: your-registry/order-backend:latest
            ports:
            - containerPort: 8000
            env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: order-secrets
                  key: database-url
            - name: SECRET_KEY
              valueFrom:
                secretKeyRef:
                  name: order-secrets
                  key: secret-key
            resources:
              requests:
                memory: "256Mi"
                cpu: "250m"
              limits:
                memory: "512Mi"
                cpu: "500m"
            livenessProbe:
              httpGet:
                path: /health
                port: 8000
              initialDelaySeconds: 30
              periodSeconds: 10
            readinessProbe:
              httpGet:
                path: /health
                port: 8000
              initialDelaySeconds: 5
              periodSeconds: 5
    
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: order-backend-service
    spec:
      selector:
        app: order-backend
      ports:
        - protocol: TCP
          port: 80
          targetPort: 8000
      type: LoadBalancer
    ```

### Google Cloud Platform

```yaml
# Cloud Run deployment
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: order-backend
  annotations:
    run.googleapis.com/ingress: all
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/maxScale: "10"
        run.googleapis.com/cpu-throttling: "false"
        run.googleapis.com/memory: "1Gi"
    spec:
      containers:
      - image: gcr.io/your-project/order-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: order-secrets
              key: database-url
        resources:
          limits:
            cpu: 1000m
            memory: 1Gi
```

### Azure Deployment

```yaml
# Azure Container Instances
apiVersion: 2019-12-01
location: eastus
name: order-system
properties:
  containers:
  - name: order-backend
    properties:
      image: your-registry.azurecr.io/order-backend:latest
      ports:
      - port: 8000
        protocol: TCP
      environmentVariables:
      - name: DATABASE_URL
        secureValue: your-database-connection-string
      - name: SECRET_KEY
        secureValue: your-secret-key
      resources:
        requests:
          cpu: 1
          memoryInGb: 1
  - name: order-frontend
    properties:
      image: your-registry.azurecr.io/order-frontend:latest
      ports:
      - port: 8501
        protocol: TCP
      resources:
        requests:
          cpu: 0.5
          memoryInGb: 0.5
  ipAddress:
    type: Public
    ports:
    - port: 8000
      protocol: TCP
    - port: 8501
      protocol: TCP
  osType: Linux
  restartPolicy: Always
```

## 🔐 Security Configuration

### Environment Variables

**Production `.env`:**
```env
# Application Configuration
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info

# Security
SECRET_KEY=your-256-bit-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=postgresql://user:password@db-host:5432/orders
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Redis
REDIS_URL=redis://redis-host:6379/0
REDIS_PASSWORD=your-redis-password

# External Services
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Monitoring
SENTRY_DSN=https://your-sentry-dsn
DATADOG_API_KEY=your-datadog-key

# SSL/TLS
SSL_CERT_PATH=/etc/ssl/certs/cert.pem
SSL_KEY_PATH=/etc/ssl/private/key.pem
```

### SSL Certificate Setup

=== "Let's Encrypt"
    ```bash
    # Install Certbot
    sudo apt-get update
    sudo apt-get install certbot python3-certbot-nginx
    
    # Obtain certificate
    sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
    
    # Auto-renewal
    sudo crontab -e
    # Add: 0 12 * * * /usr/bin/certbot renew --quiet
    ```

=== "Custom Certificate"
    ```bash
    # Generate private key
    openssl genrsa -out private.key 2048
    
    # Generate certificate signing request
    openssl req -new -key private.key -out request.csr
    
    # Install certificate
    sudo cp certificate.crt /etc/ssl/certs/
    sudo cp private.key /etc/ssl/private/
    sudo chmod 600 /etc/ssl/private/private.key
    ```

### Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# iptables
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
sudo iptables -P INPUT DROP
```

## 📊 Performance Optimization

### Database Optimization

```sql
-- Create indexes for better performance
CREATE INDEX idx_pedidos_usuario ON pedidos(usuario);
CREATE INDEX idx_pedidos_status ON pedidos(status);
CREATE INDEX idx_pedidos_data_criacao ON pedidos(data_criacao);
CREATE INDEX idx_itens_pedido ON itens(pedido_id);

-- Optimize queries
EXPLAIN ANALYZE SELECT * FROM pedidos WHERE usuario = 1;

-- Connection pooling
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
```

### Application Performance

**`backend/config.py` (Production Settings):**
```python
# Production configuration
class ProductionConfig:
    # Database connection pooling
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'max_overflow': 30,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }
    
    # Caching
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.getenv('REDIS_URL')
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL')
    RATELIMIT_DEFAULT = "100/hour"
    
    # Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
```

### CDN Configuration

```yaml
# CloudFront distribution
Resources:
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        Origins:
          - Id: OrderSystemOrigin
            DomainName: !GetAtt ALB.DNSName
            CustomOriginConfig:
              HTTPPort: 80
              HTTPSPort: 443
              OriginProtocolPolicy: redirect-to-https
        DefaultCacheBehavior:
          TargetOriginId: OrderSystemOrigin
          ViewerProtocolPolicy: redirect-to-https
          CachePolicyId: 4135ea2d-6df8-44a3-9df3-4b5a84be39ad
        CacheBehaviors:
          - PathPattern: "/api/*"
            TargetOriginId: OrderSystemOrigin
            ViewerProtocolPolicy: redirect-to-https
            CachePolicyId: 4135ea2d-6df8-44a3-9df3-4b5a84be39ad
            TTL: 0
        Enabled: true
        HttpVersion: http2
        ViewerCertificate:
          AcmCertificateArn: !Ref SSLCertificate
          SslSupportMethod: sni-only
```

## 🔍 Monitoring & Alerting

### Application Monitoring

**Prometheus Configuration:**
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'order-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: /metrics
    
  - job_name: 'order-frontend'
    static_configs:
      - targets: ['frontend:8501']
    metrics_path: /metrics

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
```

**Grafana Dashboard:**
```json
{
  "dashboard": {
    "title": "Order Management System",
    "panels": [
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "http_request_duration_seconds{job=\"order-backend\"}"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])"
          }
        ]
      }
    ]
  }
}
```

### Log Management

**ELK Stack Configuration:**
```yaml
# docker-compose.monitoring.yml
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.8.0
    environment:
      - discovery.type=single-node
      - ES_JAVA_OPTS=-Xms512m -Xmx512m
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  logstash:
    image: docker.elastic.co/logstash/logstash:8.8.0
    volumes:
      - ./logstash/pipeline:/usr/share/logstash/pipeline
      - ./logs:/usr/share/logstash/logs
    depends_on:
      - elasticsearch

  kibana:
    image: docker.elastic.co/kibana/kibana:8.8.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch
```

### Health Checks & Alerts

```python
# Backend health check endpoint
@app.get("/health")
async def health_check():
    try:
        # Database health
        db_health = await check_database_connection()
        
        # Redis health
        redis_health = await check_redis_connection()
        
        # External services
        external_health = await check_external_services()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {
                "database": db_health,
                "redis": redis_health,
                "external": external_health
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
```

## 🚀 Deployment Pipeline

### CI/CD with GitHub Actions

**`.github/workflows/deploy.yml`:**
```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r backend/requirements.txt
        pip install -r frontend/requirements.txt
    
    - name: Run tests
      run: |
        pytest backend/tests/
        pytest frontend/tests/
    
    - name: Run security scan
      run: |
        pip install bandit
        bandit -r backend/
        bandit -r frontend/

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ secrets.REGISTRY_URL }}
        username: ${{ secrets.REGISTRY_USERNAME }}
        password: ${{ secrets.REGISTRY_PASSWORD }}
    
    - name: Build and push backend
      uses: docker/build-push-action@v4
      with:
        context: ./backend
        push: true
        tags: ${{ secrets.REGISTRY_URL }}/order-backend:${{ github.sha }}
    
    - name: Build and push frontend
      uses: docker/build-push-action@v4
      with:
        context: ./frontend
        push: true
        tags: ${{ secrets.REGISTRY_URL }}/order-frontend:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment: production
    steps:
    - name: Deploy to production
      run: |
        echo "Deploying to production..."
        # Add your deployment commands here
```

## 🛡️ Backup & Disaster Recovery

### Database Backup

```bash
#!/bin/bash
# backup-database.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DATABASE_URL="postgresql://user:password@host:5432/orders"

# Create backup
pg_dump $DATABASE_URL > "$BACKUP_DIR/orders_backup_$DATE.sql"

# Compress backup
gzip "$BACKUP_DIR/orders_backup_$DATE.sql"

# Upload to S3
aws s3 cp "$BACKUP_DIR/orders_backup_$DATE.sql.gz" s3://your-backup-bucket/

# Cleanup old backups (keep last 7 days)
find $BACKUP_DIR -name "orders_backup_*.sql.gz" -mtime +7 -delete
```

### Application Backup

```bash
#!/bin/bash
# backup-application.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# Backup configuration
tar -czf "$BACKUP_DIR/config_backup_$DATE.tar.gz" \
    .env \
    docker-compose.yml \
    nginx/ \
    ssl/

# Backup tokens directory
tar -czf "$BACKUP_DIR/tokens_backup_$DATE.tar.gz" backend/tokens/

# Upload to cloud storage
aws s3 sync $BACKUP_DIR s3://your-backup-bucket/application/
```

### Disaster Recovery Plan

1. **Database Recovery**
   ```bash
   # Restore from backup
   gunzip -c orders_backup_20231201_120000.sql.gz | psql $DATABASE_URL
   ```

2. **Application Recovery**
   ```bash
   # Restore configuration
   tar -xzf config_backup_20231201_120000.tar.gz
   
   # Restart services
   docker-compose down
   docker-compose up -d
   ```

3. **Verification**
   ```bash
   # Check service health
   curl -f http://localhost:8000/health
   curl -f http://localhost:8501/_stcore/health
   ```

---

## 🎯 Production Checklist

### Pre-Deployment

- [ ] **Security audit** completed
- [ ] **Load testing** performed
- [ ] **Database migrations** tested
- [ ] **Backup strategy** implemented
- [ ] **Monitoring** configured
- [ ] **SSL certificates** installed
- [ ] **Firewall rules** configured
- [ ] **Environment variables** secured

### Post-Deployment

- [ ] **Health checks** passing
- [ ] **Monitoring** alerts configured
- [ ] **Backup schedule** verified
- [ ] **Performance metrics** baseline established
- [ ] **Documentation** updated
- [ ] **Team training** completed

---

**🎉 Congratulations! Your Order Management System is now production-ready!** 🚀

**Next:** [Contributing Guide](../contributing.md) 🤝