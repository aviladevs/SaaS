# 🚀 High-Load Infrastructure Configuration

This directory contains optimized infrastructure configurations for the Ávila DevOps SaaS platform to support **1000+ concurrent requests per second**.

## 📊 Performance Targets

- **Current Capacity**: ~330 req/s
- **Target Capacity**: 1000+ req/s
- **Stretch Goal**: 1500 req/s
- **Response Time**: <300ms (p95)
- **Error Rate**: <1%

## 📁 Directory Structure

```
infrastructure/
├── nginx/
│   └── saas.high-load.conf      # Optimized Nginx configuration
└── kubernetes/
    └── saas-high-load.yaml      # High-load Kubernetes deployment
```

## 🔧 Components

### 1. Nginx Configuration (`nginx/saas.high-load.conf`)

**Key Optimizations:**
- ✅ Worker connections increased to **8192** (from 2048)
- ✅ Rate limiting optimized to **500 req/s** per zone
- ✅ Connection pooling with **64 keepalive connections** per upstream
- ✅ Intelligent caching with Redis-like behavior
- ✅ HTTP/2 with connection reuse
- ✅ Multiple upstream servers (5 per service)
- ✅ Optimized buffer sizes and timeouts

**Features:**
- Smart proxy caching for GET requests (5-minute TTL)
- Static file caching with 1-year expiry
- Health checks and monitoring endpoints
- WebSocket support for real-time features
- CORS headers for API endpoints
- Security headers (CSP, HSTS, XSS protection)

**Deployment:**
```bash
# Copy to Nginx config directory
sudo cp infrastructure/nginx/saas.high-load.conf /etc/nginx/nginx.conf

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### 2. Kubernetes Configuration (`kubernetes/saas-high-load.yaml`)

**Key Components:**

#### Database Infrastructure
- **PostgreSQL Master-Slave**: 1 master + 2 read replicas
- **PgBouncer**: Connection pooling (10,000 max client connections)
- **Pool mode**: Transaction-level pooling for optimal performance

#### Redis Cluster
- **6 Redis instances** in cluster mode
- **2GB memory** per instance
- Configured for high availability and data persistence

#### Application Deployments
Each service is configured with:
- **Minimum replicas**: 5-10 per service
- **Maximum replicas**: 40-50 per service
- **HPA (Horizontal Pod Autoscaler)**:
  - CPU target: 70%
  - Memory target: 80%
  - Scale-up: Add 50% or 5 pods per minute (whichever is larger)
  - Scale-down: Remove 10% per minute (gradual)

#### Service Configuration
| Service | Min Replicas | Max Replicas | Memory Request | CPU Request |
|---------|--------------|--------------|----------------|-------------|
| landing-page | 10 | 50 | 512Mi | 500m |
| recycling-system | 10 | 50 | 768Mi | 750m |
| fiscal-system | 10 | 50 | 768Mi | 750m |
| main-app | 10 | 50 | 768Mi | 750m |
| clinica-system | 8 | 40 | 512Mi | 500m |

#### Monitoring Stack
- **Prometheus**: Metrics collection from all services
- **Grafana**: Dashboards and visualization
- **Exporters**: PostgreSQL, Redis, Nginx metrics

**Deployment:**
```bash
# Apply Kubernetes configuration
kubectl apply -f infrastructure/kubernetes/saas-high-load.yaml

# Monitor deployment
kubectl get pods -n aviladevops-saas -w

# Check HPA status
kubectl get hpa -n aviladevops-saas
```

## 🧪 Load Testing

Load testing scripts are available in `/scripts/setup/`:

### Using k6 (Recommended)

**Prerequisites:**
```bash
# Install k6
# macOS
brew install k6

# Ubuntu/Debian
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6

# Windows
choco install k6
# or
winget install k6
```

**Run Load Test:**

```bash
# Using bash script (Linux/macOS)
cd scripts/setup
BASE_URL=https://aviladevops.com.br ./run-load-tests.sh

# Using PowerShell (Windows)
cd scripts/setup
.\load-test.ps1 -BaseUrl "https://aviladevops.com.br"

# Direct k6 execution
k6 run --out json=results.json scripts/setup/load-test-k6.js
```

**Test Stages:**
1. Warm-up: 0 → 100 → 300 users (5 minutes)
2. Baseline: 500 users (15 minutes)
3. Target load: 1000 users (13 minutes)
4. Stress test: 1500 users (7 minutes)
5. Cool down: 1500 → 0 users (4 minutes)

**Total Duration**: ~45 minutes

## 📈 Monitoring

### Prometheus Metrics

Access Prometheus at: `http://prometheus-service:9090`

Key metrics to monitor:
- `http_requests_total`: Total HTTP requests
- `http_request_duration_seconds`: Request latency
- `http_requests_failed_total`: Failed requests
- `nginx_connections_active`: Active connections
- `postgres_connections`: Database connections
- `redis_connected_clients`: Redis connections

### Grafana Dashboards

Access Grafana at: `http://grafana-service:3000`

Pre-configured dashboards:
- System Overview
- Application Performance
- Database Performance
- Cache Hit Rates
- Error Rates

### Health Checks

```bash
# Nginx status
curl http://your-domain/nginx-status

# Application health
curl http://your-domain/health

# Prometheus metrics
curl http://your-domain:9091/metrics
```

## 🎯 Performance Tuning Tips

### 1. Operating System Tuning

```bash
# Increase file descriptors
sudo sysctl -w fs.file-max=2097152
sudo sysctl -w fs.nr_open=2097152

# TCP tuning
sudo sysctl -w net.core.somaxconn=65535
sudo sysctl -w net.ipv4.tcp_max_syn_backlog=8192
sudo sysctl -w net.ipv4.ip_local_port_range="1024 65535"

# Make permanent
echo "fs.file-max = 2097152" | sudo tee -a /etc/sysctl.conf
echo "net.core.somaxconn = 65535" | sudo tee -a /etc/sysctl.conf
```

### 2. PostgreSQL Tuning

```sql
-- In postgresql.conf
max_connections = 500
shared_buffers = 4GB
effective_cache_size = 12GB
work_mem = 16MB
maintenance_work_mem = 512MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
```

### 3. Redis Tuning

```conf
# In redis.conf
maxmemory 4gb
maxmemory-policy allkeys-lru
tcp-backlog 511
timeout 0
tcp-keepalive 300
```

### 4. Application Tuning

```bash
# Gunicorn (Python/Django apps)
gunicorn \
  --workers 4 \
  --threads 2 \
  --worker-class gthread \
  --timeout 30 \
  --keep-alive 5 \
  --max-requests 10000 \
  --max-requests-jitter 1000

# Node.js (Next.js apps)
NODE_OPTIONS="--max-old-space-size=2048"
UV_THREADPOOL_SIZE=128
```

## 🚨 Troubleshooting

### High Response Times

1. Check database connection pool utilization
2. Verify cache hit rates
3. Monitor CPU/Memory usage
4. Check for slow queries
5. Verify network latency

### High Error Rates

1. Check application logs
2. Verify database connectivity
3. Check Redis connectivity
4. Monitor disk I/O
5. Check for OOM kills

### Scaling Issues

1. Verify HPA is configured correctly
2. Check resource limits
3. Monitor pod startup times
4. Verify node capacity
5. Check cluster autoscaler logs

## 📚 Additional Resources

- [Nginx Performance Tuning](https://www.nginx.com/blog/tuning-nginx/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [PostgreSQL Performance Tips](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [Redis Best Practices](https://redis.io/docs/manual/optimization/)
- [k6 Documentation](https://k6.io/docs/)

## 🤝 Contributing

When making changes to infrastructure:

1. Test in development environment first
2. Run load tests to validate changes
3. Update documentation
4. Create pull request with performance metrics

## 📞 Support

For issues or questions:
- Create an issue in the repository
- Contact the DevOps team
- Check monitoring dashboards

---

**Last Updated**: 2024
**Maintained by**: Ávila DevOps Team
