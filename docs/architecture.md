# 🏗️ Arquitetura - Ávila DevOps SaaS

## 📊 Diagrama da Arquitetura

```mermaid
graph TB
    %% Load Balancer
    LB[Nginx Load Balancer<br/>SSL/TLS + Rate Limiting]

    %% Serviços Frontend
    LP[Landing Page<br/>Django + PostgreSQL]
    CL[Clínica Management<br/>Next.js + TypeScript]

    %% Serviços Backend
    SYS[Sistema Reciclagem<br/>Django + ML]
    FIS[Sistema Fiscal<br/>Django + Analytics]
    ADM[Admin Dashboard<br/>Django + Multi-tenant]

    %% Infraestrutura
    DB[(PostgreSQL<br/>Multi-tenant)]
    REDIS[(Redis<br/>Cache + Celery)]
    ES[(Elasticsearch<br/>Busca + Logs)]

    %% Monitoramento
    GRAF[Grafana<br/>Dashboards]
    PROM[Prometheus<br/>Métricas]
    SENTRY[Sentry<br/>Error Tracking]

    %% Usuários
    USER1[👤 Usuário<br/>Empresa A]
    USER2[👥 Usuários<br/>Empresa B]

    %% Conexões Externas
    GOOGLE[Google Cloud<br/>Storage + CDN]
    GITHUB[GitHub<br/>CI/CD]

    %% Fluxo Principal
    USER1 --> LB
    USER2 --> LB

    LB --> LP
    LB --> CL
    LB --> SYS
    LB --> FIS
    LB --> ADM

    %% Conexões de Dados
    LP --> DB
    SYS --> DB
    FIS --> DB
    ADM --> DB

    CL --> ADM

    %% Cache e Background Jobs
    LP --> REDIS
    SYS --> REDIS
    FIS --> REDIS
    ADM --> REDIS

    %% Busca e Logs
    LP --> ES
    SYS --> ES
    FIS --> ES
    ADM --> ES

    %% Monitoramento
    LP --> PROM
    SYS --> PROM
    FIS --> PROM
    ADM --> PROM
    DB --> PROM
    REDIS --> PROM

    PROM --> GRAF
    ES --> GRAF

    LP --> SENTRY
    SYS --> SENTRY
    FIS --> SENTRY
    ADM --> SENTRY

    %% Integrações Externas
    ADM -.-> GOOGLE
    SYS -.-> GOOGLE

    %% CI/CD
    GITHUB -.-> LP
    GITHUB -.-> SYS
    GITHUB -.-> FIS
    GITHUB -.-> CL
    GITHUB -.-> ADM
```

## 🏢 Arquitetura Multi-tenant

### **Isolamento por Tenant**
Cada cliente possui ambiente completamente isolado:

```
🌐 cliente-a.aviladevops.com.br
├── 🗄️  Database Schema: tenant_a
├── 👥  Users: cliente_a_*
├── 📁  Files: /media/tenant_a/
└── ⚙️  Config: settings específicas

🌐 cliente-b.aviladevops.com.br
├── 🗄️  Database Schema: tenant_b
├── 👥  Users: cliente_b_*
├── 📁  Files: /media/tenant_b/
└── ⚙️  Config: settings específicas
```

### **Camadas de Segurança**

#### **1. Network Level**
```yaml
# Firewall rules
- Source: 0.0.0.0/0 (restrito por serviço)
- Protocol: TCP
- Ports: 80, 443 (HTTPS only)
- Rate limiting: 1000 req/min per IP
```

#### **2. Application Level**
```python
# Django settings
TENANT_MODEL = 'users.Tenant'
TENANT_ID_FIELD = 'tenant_id'

# Middleware para isolamento
class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Identificar tenant pelo domínio
        hostname = request.get_host().split(':')[0]
        tenant = Tenant.objects.get(domain=hostname)

        # Configurar request para tenant
        request.tenant = tenant
        return self.get_response(request)
```

#### **3. Database Level**
```sql
-- Row Level Security (RLS) no PostgreSQL
ALTER TABLE services ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON services
    FOR ALL USING (tenant_id = current_setting('app.current_tenant'));
```

## 🚀 Fluxos de Dados

### **Fluxo de Autenticação**
```mermaid
sequenceDiagram
    participant U as Usuário
    participant LB as Load Balancer
    participant ADM as Admin Service
    participant DB as Database
    participant REDIS as Redis

    U->>LB: POST /api/auth/login/
    LB->>ADM: Proxy request
    ADM->>DB: Verificar credenciais
    DB-->>ADM: Usuário válido
    ADM->>REDIS: Gerar JWT token
    REDIS-->>ADM: Token criado
    ADM-->>LB: Retornar token
    LB-->>U: JWT + refresh token
```

### **Fluxo de Criação de Tenant**
```mermaid
sequenceDiagram
    participant DEV as Developer
    participant GH as GitHub Actions
    participant GCP as Google Cloud
    participant DB as Database

    DEV->>GH: Workflow tenant-management
    GH->>GCP: Provisionar recursos
    GCP-->>GH: Recursos criados
    GH->>DB: Executar migrações
    DB-->>GH: Schema criado
    GH-->>DEV: Notificação de sucesso
```

## 📊 Monitoramento e Observabilidade

### **Métricas Coletadas**

#### **Application Metrics**
- Request count e latency por endpoint
- Error rates por serviço
- Database query performance
- Cache hit/miss ratios

#### **Infrastructure Metrics**
- CPU, memória e disco por serviço
- Network I/O e throughput
- Database connections e performance
- Redis memory usage

#### **Business Metrics**
- Usuários ativos por tenant
- Feature usage analytics
- Revenue tracking
- Support ticket metrics

### **Dashboards**

#### **📈 Application Health**
```yaml
# Prometheus Queries
uptime = time() - process_start_time_seconds
error_rate = rate(errors_total[5m]) / rate(requests_total[5m])
response_time_p95 = histogram_quantile(0.95, rate(response_time_seconds_bucket[5m]))
db_connection_pool = db_connections_active / db_connections_max
```

#### **💰 Business KPIs**
```yaml
# Métricas de negócio
active_users = sum(ga_active_users) by (tenant)
conversion_rate = sum(purchases) / sum(visits) * 100
revenue_mrr = sum(subscription_revenue) by (tenant)
support_tickets = sum(tickets_created) - sum(tickets_resolved)
```

## 🔒 Modelo de Segurança

### **Autenticação Multi-camadas**

#### **JWT + Refresh Tokens**
```python
# Configuração Django
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}
```

#### **Tenant-based Authorization**
```python
# Middleware personalizado
class TenantPermission(BasePermission):
    def has_permission(self, request, view):
        # Verificar se usuário pertence ao tenant correto
        return request.user.tenant == request.tenant
```

### **Criptografia de Dados**

#### **Dados em Repouso**
- **Banco de dados**: PostgreSQL com encryption at rest
- **Backups**: Criptografados com AES-256
- **Files**: Cloud Storage com server-side encryption

#### **Dados em Trânsito**
- **HTTPS**: TLS 1.3 obrigatório
- **API interna**: mTLS entre serviços
- **Database**: SSL/TLS para conexões

## 🚀 Estratégia de Deploy

### **Ambientes**

#### **Desenvolvimento**
- **Local**: Docker Compose com serviços individuais
- **CI**: GitHub Actions com testes automatizados
- **CDN**: Não utilizado (desenvolvimento)

#### **Staging**
- **Infra**: Kubernetes namespace separado
- **Dados**: Database schema staging
- **CDN**: Domínio staging.aviladevops.com.br

#### **Produção**
- **Infra**: Multi-region Google Cloud
- **Dados**: Database schemas isolados por tenant
- **CDN**: Global com cache inteligente

### **Estratégia de Release**

#### **Blue-Green Deployment**
```yaml
# Kubernetes deployment
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 1
    maxSurge: 1
```

#### **Canary Releases**
```yaml
# Traffic splitting para validação
- 90% tráfego: versão atual
- 10% tráfego: nova versão
# Monitorar métricas por 24h antes de promover
```

## 📈 Escalabilidade

### **Auto-scaling**

#### **Horizontal Pod Autoscaler**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: saas-scaler
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: main-app
  minReplicas: 3
  maxReplicas: 50
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

#### **Database Scaling**
- **Read replicas**: Para consultas de leitura
- **Connection pooling**: PgBouncer para otimização
- **Sharding**: Por tenant (planejado para futuro)

### **Performance Optimization**

#### **Caching Strategy**
- **CDN**: Static assets (CSS, JS, imagens)
- **Redis**: Sessions, API responses, computed data
- **Database**: Query results e materialized views

#### **Database Optimization**
- **Indexes**: Estratégicos por tenant e consulta comum
- **Query optimization**: EXPLAIN ANALYZE para slow queries
- **Connection pooling**: Configurado para alta concorrência

## 🔧 Desenvolvimento e DevOps

### **CI/CD Pipeline**

#### **GitHub Actions Workflow**
```yaml
name: SaaS Deployment Pipeline
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: make test

  deploy-staging:
    needs: test
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to staging
        run: make deploy-staging

  deploy-production:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: make deploy-prod
```

### **Code Quality**

#### **Linting e Formatação**
```yaml
# Python
black --check .
isort --check-only .
flake8 .
mypy .

# JavaScript/TypeScript
eslint .
prettier --check .

# Docker
hadolint Dockerfile*
```

#### **Security Scanning**
```yaml
# Dependências
safety check
npm audit

# Containers
trivy image app-image:latest

# Application
zap-baseline.py -t http://localhost:8000
```

## 🚀 High-Load Architecture (1000+ req/s)

### **Performance Targets**
- **Current Capacity**: ~330 req/s
- **Target Capacity**: 1000+ req/s
- **Stretch Goal**: 1500 req/s
- **Response Time**: <300ms (p95)
- **Error Rate**: <1%

### **Infrastructure Optimizations**

#### **Nginx Configuration**
```nginx
# Key optimizations implemented
worker_connections 8192;              # Increased from 2048
keepalive 64;                         # Connection pooling per upstream
limit_req_zone ... rate=500r/s;       # Optimized rate limiting
proxy_cache api_cache;                # Intelligent caching
```

**Features:**
- 5 backend instances per service
- Smart proxy caching (5-minute TTL for GET requests)
- Static file caching (1-year expiry)
- HTTP/2 with connection reuse

#### **Kubernetes Auto-scaling**
```yaml
# HPA Configuration per service
minReplicas: 10                       # Increased from 3
maxReplicas: 50                       # Increased from 10
targetCPUUtilization: 70%
targetMemoryUtilization: 80%
```

**Scale-up Policy:**
- Add 50% or 5 pods per minute (whichever is larger)
- Stabilization window: 60 seconds

**Scale-down Policy:**
- Remove 10% per minute
- Stabilization window: 300 seconds

#### **Database High-Availability**

**PostgreSQL Configuration:**
- 1 Master instance (2Gi memory, 2 CPU)
- 2 Read Replicas (1Gi memory, 1 CPU each)
- PgBouncer connection pooling:
  - Max client connections: 10,000
  - Default pool size: 100 per database
  - Pool mode: transaction-level

**Performance Settings:**
```sql
max_connections = 500
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 16MB
```

#### **Redis Cluster**
- 6 Redis instances in cluster mode
- 2GB memory per instance
- Configured for high availability
- LRU eviction policy
- AOF persistence enabled

### **Monitoring Stack**

#### **Prometheus Metrics**
- Request rate and latency tracking
- Error rate monitoring
- Database connection pool metrics
- Redis operations tracking
- Pod CPU/Memory utilization

#### **Grafana Dashboards**
- Real-time performance overview
- Service-level metrics
- Database and cache performance
- Alert visualization

#### **Alert Rules**
- High error rate (>1%)
- High response time (p95 >300ms)
- Database connection pool exhaustion
- Redis memory pressure
- HPA max replicas reached

### **Load Testing**

Automated load testing with k6:
```bash
# Run load test
cd scripts/setup
BASE_URL=https://your-domain.com ./run-load-tests.sh
```

**Test Stages:**
1. Warm-up: 0 → 300 users (5 min)
2. Baseline: 500 users (15 min)
3. Target: 1000 users (13 min)
4. Stress: 1500 users (7 min)
5. Cool-down: 1500 → 0 users (4 min)

### **Deployment Guide**

Complete high-load deployment instructions available in:
- [📖 Infrastructure README](../infrastructure/README.md)
- [🚀 Deployment Guide](../infrastructure/DEPLOYMENT.md)

**Quick Start:**
```bash
# 1. Apply Kubernetes configuration
kubectl apply -f infrastructure/kubernetes/saas-high-load.yaml

# 2. Deploy Nginx configuration
sudo cp infrastructure/nginx/saas.high-load.conf /etc/nginx/nginx.conf
sudo nginx -s reload

# 3. Run load tests
./scripts/setup/run-load-tests.sh
```

## 📚 Recursos e Links

### **Documentação Técnica**
- [🐳 Docker Docs](./docker/)
- [☸️ Kubernetes Configs](./kubernetes/)
- [🏗️ Terraform Infra](./terraform/)
- [📊 Monitoring Setup](./monitoring/)
- [🚀 High-Load Infrastructure](../infrastructure/)

### **Ferramentas e Serviços**
- [🔧 Django Admin](https://docs.djangoproject.com/en/stable/ref/contrib/admin/)
- [📖 Django REST Framework](https://www.django-rest-framework.org/)
- [⚛️ Next.js Docs](https://nextjs.org/docs)
- [☁️ Google Cloud](https://cloud.google.com/docs)
- [📈 k6 Load Testing](https://k6.io/docs/)

### **Comunidade**
- [💬 Discord Dev](https://discord.gg/avila-devops-dev)
- [🐛 GitHub Issues](https://github.com/avila-devops/saas/issues)
- [📋 GitHub Projects](https://github.com/avila-devops/saas/projects)

---

**🏗️ Arquitetura sólida para crescimento sustentável** | **Ávila DevOps**
