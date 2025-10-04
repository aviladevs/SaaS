# 📊 Monitoring Stack - Quick Reference

## 🚀 Quick Start

```bash
# Start monitoring stack
make monitor

# Or use the script directly
bash monitoring/start-monitoring.sh
```

## 🌐 Access URLs

| Service | URL | Credentials | Purpose |
|---------|-----|-------------|---------|
| **Grafana** | http://localhost:3001 | admin/admin | Dashboards & Visualization |
| **Prometheus** | http://localhost:9090 | - | Metrics Database |
| **AlertManager** | http://localhost:9093 | - | Alert Management |
| **Kibana** | http://localhost:5601 | - | Log Analysis |
| **Elasticsearch** | http://localhost:9200 | - | Log Storage |
| **Jaeger** | http://localhost:16686 | - | Distributed Tracing |
| **Flower** | http://localhost:5555 | admin/admin | Celery Monitoring |
| **cAdvisor** | http://localhost:8080 | - | Container Metrics |

## 📈 Grafana Dashboards

Pre-configured dashboards available in Grafana:

1. **Application Health** - Service uptime, error rates, response times
2. **Business KPIs** - User metrics, revenue, conversions
3. **Infrastructure** - CPU, memory, disk, network
4. **Performance** - Latency, throughput, database performance
5. **Executive Overview** - High-level business and technical metrics
6. **SLA Monitoring** - SLA compliance, error budget, incidents

## 🔔 Alert Severity Levels

| Severity | Description | Response Time | Notification |
|----------|-------------|---------------|--------------|
| **Critical** 🚨 | Service down, SLA violation | Immediate | PagerDuty + Slack |
| **Warning** ⚠️ | Degraded performance | < 30 minutes | Slack |

## 📊 Key Metrics

### Application Metrics
```promql
# Request rate
rate(django_http_requests_total[5m])

# Error rate
rate(django_http_responses_total_by_status_total{status=~"5.."}[5m])

# P95 latency
histogram_quantile(0.95, rate(django_http_request_duration_seconds_bucket[5m]))
```

### Infrastructure Metrics
```promql
# CPU usage
100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory usage
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# Disk usage
(1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100
```

### Business Metrics
```promql
# Active users
saas_active_users_total

# User registrations (24h)
increase(saas_user_registrations_total[24h])

# Revenue
sum(saas_revenue_total) by (tenant)
```

## 🎯 SLA Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Uptime** | 99.9% | Monthly |
| **Response Time (P95)** | < 300ms | 5-minute window |
| **Error Rate** | < 0.1% | 5-minute window |
| **MTTR** | < 15 minutes | Per incident |

## 🔧 Common Commands

```bash
# Start monitoring
make monitor

# Stop monitoring
make monitor-stop

# Restart monitoring
make monitor-restart

# View status
make monitor-status

# View logs
make monitor-logs

# Health check
make monitor-health

# View specific service logs
docker-compose -f docker-compose.monitoring.yml logs -f prometheus
```

## 🔍 Troubleshooting

### Services Not Starting

```bash
# Check service status
make monitor-status

# View logs for specific service
docker-compose -f docker-compose.monitoring.yml logs <service-name>

# Restart specific service
docker-compose -f docker-compose.monitoring.yml restart <service-name>
```

### Prometheus Not Scraping

1. Check targets: http://localhost:9090/targets
2. Verify service is running and metrics endpoint is accessible
3. Check Prometheus configuration: `monitoring/prometheus/prometheus.yml`

### Grafana Dashboard Empty

1. Verify Prometheus data source: Grafana → Configuration → Data Sources
2. Check if metrics exist in Prometheus: http://localhost:9090/graph
3. Verify time range selection in dashboard

### Elasticsearch Issues

```bash
# Check cluster health
curl http://localhost:9200/_cluster/health?pretty

# Check indices
curl http://localhost:9200/_cat/indices?v

# Clear old indices
curl -X DELETE "localhost:9200/logstash-2024.01.*"
```

## 📝 Integration

### Django Applications

```python
# Install packages
pip install prometheus-client django-prometheus

# Add to settings.py
INSTALLED_APPS = ['django_prometheus', ...]
MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    # ... other middleware
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

# Add to urls.py
urlpatterns = [
    path('', include('django_prometheus.urls')),
    # ... other paths
]
```

### Next.js Applications

```bash
# Install package
npm install prom-client

# Create health endpoints
# pages/api/health.ts
# pages/api/metrics.ts
```

See `monitoring/INTEGRATION_GUIDE.md` for complete instructions.

## 🔐 Security

**Change default passwords:**
- Grafana: admin/admin → http://localhost:3001/profile/password
- Flower: admin/admin → Update in `.env`

**Configure alerts:**
- Update `monitoring/.env` with your Slack webhook and PagerDuty keys

## 📚 Documentation

- **Main Guide**: `monitoring/README.md`
- **Integration Guide**: `monitoring/INTEGRATION_GUIDE.md`
- **Configuration**: `monitoring/prometheus/`, `monitoring/grafana/`, etc.

## 🆘 Support

- Repository Issues: https://github.com/aviladevs/SaaS/issues
- Email: devops@aviladevops.com.br
- Slack: #saas-monitoring

## 📦 Stack Components

- **Prometheus** - Metrics collection and storage
- **Grafana** - Visualization and dashboards
- **AlertManager** - Alert routing and notifications
- **Elasticsearch** - Log storage
- **Logstash** - Log processing
- **Kibana** - Log visualization
- **Jaeger** - Distributed tracing
- **Node Exporter** - System metrics
- **Postgres Exporter** - Database metrics
- **Redis Exporter** - Cache metrics
- **Nginx Exporter** - Web server metrics
- **cAdvisor** - Container metrics
- **Flower** - Celery task monitoring

## 🎯 What's Monitored

- ✅ Application health and uptime
- ✅ Request rates and latency
- ✅ Error rates and types
- ✅ Database performance
- ✅ Cache hit rates
- ✅ Infrastructure resources (CPU, memory, disk)
- ✅ Container metrics
- ✅ Business KPIs (users, revenue, conversions)
- ✅ Celery task execution
- ✅ Distributed traces
- ✅ Centralized logs
- ✅ SLA compliance
