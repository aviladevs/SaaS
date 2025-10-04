# 📊 Monitoring & Observability Stack - Ávila DevOps SaaS

## 🎯 Overview

Complete monitoring and observability solution for the Ávila DevOps SaaS platform, providing comprehensive visibility into application health, infrastructure performance, business metrics, and user behavior.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Applications                              │
│  Landing Page │ Sistema │ Fiscal │ Clínica │ Main App          │
└────────┬────────────────┬─────────────────┬─────────────────────┘
         │                │                 │
         ▼                ▼                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Metrics Collection                            │
│                      Prometheus                                  │
│  ┌──────────────┬──────────────┬──────────────┐                │
│  │ Node Exporter│ Postgres Exp │  Redis Exp   │                │
│  └──────────────┴──────────────┴──────────────┘                │
└────────┬────────────────┬─────────────────┬─────────────────────┘
         │                │                 │
         ▼                ▼                 ▼
┌─────────────────────────────────────────────────────────────────┐
│            Visualization & Alerting                              │
│  ┌──────────────┬──────────────┬──────────────┐                │
│  │   Grafana    │ AlertManager │    Flower    │                │
│  │  Dashboards  │    Alerts    │   Celery     │                │
│  └──────────────┴──────────────┴──────────────┘                │
└─────────────────────────────────────────────────────────────────┘

         ┌─────────────────────────────────────┐
         │      Logging & Tracing              │
         │  ELK Stack         Jaeger           │
         │  (Elasticsearch,   (Distributed     │
         │   Logstash,        Tracing)         │
         │   Kibana)                            │
         └─────────────────────────────────────┘
```

## 📦 Stack Components

### 1. Metrics Collection

#### **Prometheus** (Port: 9090)
- Time-series database for metrics
- Service discovery for automatic target detection
- Recording rules for pre-computed metrics
- Alert evaluation engine

#### **Exporters**
- **Node Exporter** (9100): System metrics (CPU, memory, disk, network)
- **Postgres Exporter** (9187): Database metrics and performance
- **Redis Exporter** (9121): Cache metrics and hit rates
- **Nginx Exporter** (9113): Web server metrics
- **cAdvisor** (8080): Container resource usage

### 2. Visualization

#### **Grafana** (Port: 3001)
Pre-configured dashboards:
- **Application Health**: Uptime, error rates, response times
- **Business KPIs**: User metrics, revenue, conversions
- **Infrastructure**: CPU, memory, disk, network usage
- **Performance**: Latency percentiles, throughput

Default credentials: `admin/admin` (change after first login)

### 3. Alerting

#### **AlertManager** (Port: 9093)
- Alert routing and grouping
- Notification channels: Slack, Email, PagerDuty
- Escalation policies
- Alert inhibition rules

### 4. Logging

#### **ELK Stack**
- **Elasticsearch** (9200): Log storage and indexing
- **Logstash** (5000, 5044, 5514): Log processing and enrichment
- **Kibana** (5601): Log visualization and analysis

### 5. Distributed Tracing

#### **Jaeger** (Port: 16686)
- Request tracing across microservices
- Performance bottleneck identification
- Service dependency mapping

### 6. Additional Tools

#### **Celery Flower** (Port: 5555)
- Real-time Celery task monitoring
- Task history and statistics
- Worker management

## 🚀 Quick Start

### Starting the Monitoring Stack

```bash
# Start all monitoring services
docker-compose -f docker-compose.monitoring.yml up -d

# Or using Makefile
make monitor
```

### Verify Services

```bash
# Check if all services are running
docker-compose -f docker-compose.monitoring.yml ps

# View logs
docker-compose -f docker-compose.monitoring.yml logs -f
```

### Access Dashboards

Once running, access the following URLs:

| Service | URL | Default Credentials |
|---------|-----|---------------------|
| Grafana | http://localhost:3001 | admin/admin |
| Prometheus | http://localhost:9090 | None |
| AlertManager | http://localhost:9093 | None |
| Kibana | http://localhost:5601 | None |
| Jaeger | http://localhost:16686 | None |
| Celery Flower | http://localhost:5555 | admin/admin |

## 📊 Grafana Dashboards

### 1. Application Health Dashboard

**Key Metrics:**
- Service uptime status
- Request rate (req/s)
- Error rate (%)
- Response time (P50, P95, P99)
- HTTP status code distribution
- Database connection pool usage
- Redis memory usage

**Alerts:**
- High error rate (> 0.1%)
- High response time (> 300ms)

### 2. Business KPIs Dashboard

**Key Metrics:**
- Active users
- User registrations (hourly/daily)
- Monthly Recurring Revenue (MRR)
- Conversion rate
- Churn rate
- Payment success rate
- Revenue by tenant

### 3. Infrastructure Dashboard

**Key Metrics:**
- CPU usage per instance
- Memory usage per instance
- Disk usage and I/O
- Network throughput
- Container resource usage

**Thresholds:**
- CPU warning: 80%, critical: 95%
- Memory warning: 85%, critical: 95%
- Disk warning: 85%, critical: 95%

## 🔔 Alerting Configuration

### Alert Severity Levels

1. **Critical** (🚨)
   - Service down
   - Error rate > 0.1%
   - Response time > 1s
   - Database/Redis down
   - Disk space < 5%
   - **Action**: Immediate PagerDuty + Slack notification

2. **Warning** (⚠️)
   - Elevated error rate > 0.05%
   - High response time > 300ms
   - High CPU/Memory usage > 80%
   - Low disk space < 15%
   - **Action**: Slack notification

### Notification Channels

Configure environment variables for alert routing:

```bash
# Slack
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

# PagerDuty
export PAGERDUTY_URL="https://events.pagerduty.com/v2/enqueue"
export PAGERDUTY_INTEGRATION_KEY="your-integration-key"

# Email (SMTP)
export SMTP_USER="alerts@aviladevops.com.br"
export SMTP_PASSWORD="your-password"
```

### Alert Routing

- **Critical alerts** → PagerDuty + #saas-critical Slack
- **Warning alerts** → #saas-warnings Slack
- **Business alerts** → #saas-business Slack + Email
- **Database alerts** → #saas-database Slack + DBA email
- **Infrastructure alerts** → #saas-infrastructure Slack + DevOps email

## 📝 Logging

### Log Levels

- **ERROR**: Application errors requiring attention
- **WARNING**: Potential issues to monitor
- **INFO**: Normal operational messages
- **DEBUG**: Detailed diagnostic information

### Log Structure (JSON)

```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "INFO",
  "service": "landing-page",
  "environment": "production",
  "message": "User login successful",
  "user_id": "123",
  "request_id": "abc-def-ghi",
  "trace_id": "xyz-123-456"
}
```

### Viewing Logs in Kibana

1. Navigate to http://localhost:5601
2. Go to "Discover"
3. Select index pattern: `logstash-*`
4. Filter by service, level, or search terms

### Common Queries

```
# Find all errors in the last hour
level: ERROR AND @timestamp: [now-1h TO now]

# Find errors for specific service
service: "landing-page" AND level: ERROR

# Find slow requests (> 1s)
response_time: > 1000
```

## 🔍 Distributed Tracing

### Viewing Traces in Jaeger

1. Navigate to http://localhost:16686
2. Select service from dropdown
3. Click "Find Traces"
4. Click on a trace to see detailed span information

### Trace Structure

- **Service**: Originating service name
- **Operation**: HTTP method + endpoint
- **Duration**: Total request time
- **Spans**: Individual operations within the request
- **Tags**: Metadata (HTTP status, error, user_id, etc.)

## 🎯 SLA Monitoring

### Defined SLAs

| Metric | Target | Measurement |
|--------|--------|-------------|
| Uptime | 99.9% | Monthly |
| Response Time (P95) | < 300ms | 5-minute window |
| Error Rate | < 0.1% | 5-minute window |
| MTTR | < 15 minutes | Per incident |

### SLA Dashboard

Access pre-built SLA dashboard in Grafana:
- Grafana → Dashboards → "SLA Monitoring"

Key panels:
- Current uptime percentage
- Error rate trend
- Response time percentiles
- Incident resolution time

## 🔧 Configuration

### Prometheus Configuration

Located in: `monitoring/prometheus/`
- `prometheus.yml`: Main configuration, scrape targets
- `alerts.yml`: Alert rules and thresholds
- `rules.yml`: Recording rules for pre-computed metrics

### Grafana Configuration

Located in: `monitoring/grafana/`
- `provisioning/datasources/`: Auto-configured data sources
- `provisioning/dashboards/`: Dashboard provisioning config
- `dashboards/`: JSON dashboard definitions

### ELK Configuration

Located in: `monitoring/elk/`
- `elasticsearch.yml`: Elasticsearch settings
- `logstash.conf`: Log processing pipeline
- `kibana.yml`: Kibana configuration

### Jaeger Configuration

Located in: `monitoring/jaeger/`
- `config.yml`: Tracing configuration, sampling strategy

## 📈 Custom Metrics

### Adding Application Metrics

#### Django Applications

Install prometheus-client:
```bash
pip install prometheus-client django-prometheus
```

Add to `settings.py`:
```python
INSTALLED_APPS = [
    'django_prometheus',
    # ... other apps
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    # ... other middleware
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]
```

Add to `urls.py`:
```python
from django.urls import path, include

urlpatterns = [
    path('', include('django_prometheus.urls')),
    # ... other urls
]
```

#### Custom Business Metrics

```python
from prometheus_client import Counter, Gauge, Histogram

# Counter for user registrations
user_registrations = Counter(
    'saas_user_registrations_total',
    'Total number of user registrations',
    ['tenant']
)

# Gauge for active users
active_users = Gauge(
    'saas_active_users_total',
    'Number of currently active users',
    ['tenant']
)

# Histogram for custom operation duration
operation_duration = Histogram(
    'saas_operation_duration_seconds',
    'Duration of custom operations',
    ['operation_type']
)

# Usage
user_registrations.labels(tenant='tenant1').inc()
active_users.labels(tenant='tenant1').set(150)

with operation_duration.labels(operation_type='data_export').time():
    # Your code here
    pass
```

## 🔐 Security Best Practices

1. **Change Default Passwords**
   - Update Grafana admin password immediately
   - Set strong passwords for Flower

2. **Network Security**
   - Use internal Docker network for service communication
   - Expose only necessary ports externally
   - Consider adding authentication proxy (e.g., OAuth2 Proxy)

3. **Data Retention**
   - Prometheus: 30 days (configurable)
   - Elasticsearch: Configure index lifecycle management
   - Logs: Implement retention policies based on compliance requirements

4. **Access Control**
   - Implement Grafana user roles and permissions
   - Restrict access to sensitive dashboards
   - Use read-only users for viewing dashboards

## 🔄 Backup and Maintenance

### Backup Prometheus Data

```bash
# Create snapshot
curl -XPOST http://localhost:9090/api/v1/admin/tsdb/snapshot

# Copy snapshot
docker cp saas-prometheus:/prometheus/snapshots/<snapshot-name> ./backups/
```

### Backup Grafana Dashboards

```bash
# Export all dashboards
docker exec saas-grafana grafana-cli admin export-dashboards > dashboards-backup.json
```

### Backup Elasticsearch Data

```bash
# Create snapshot repository
curl -X PUT "localhost:9200/_snapshot/backup" -H 'Content-Type: application/json' -d'
{
  "type": "fs",
  "settings": {
    "location": "/usr/share/elasticsearch/backup"
  }
}'

# Create snapshot
curl -X PUT "localhost:9200/_snapshot/backup/snapshot_1"
```

## 🐛 Troubleshooting

### Services Not Starting

```bash
# Check service status
docker-compose -f docker-compose.monitoring.yml ps

# View logs
docker-compose -f docker-compose.monitoring.yml logs <service-name>

# Restart specific service
docker-compose -f docker-compose.monitoring.yml restart <service-name>
```

### Prometheus Not Scraping Targets

1. Check Prometheus targets: http://localhost:9090/targets
2. Verify network connectivity between services
3. Ensure metrics endpoints are accessible
4. Check Prometheus configuration syntax

### Grafana Dashboard Not Loading Data

1. Verify Prometheus data source connection in Grafana
2. Check if Prometheus has data: http://localhost:9090/graph
3. Verify query syntax in dashboard panel
4. Check time range selection

### Elasticsearch Health Issues

```bash
# Check cluster health
curl http://localhost:9200/_cluster/health?pretty

# Check indices
curl http://localhost:9200/_cat/indices?v

# Clear old indices if disk space is low
curl -X DELETE "localhost:9200/logstash-2024.01.*"
```

## 📚 Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Elasticsearch Guide](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [AlertManager Configuration](https://prometheus.io/docs/alerting/latest/configuration/)

## 🤝 Support

For issues or questions:
- Create an issue in the repository
- Contact DevOps team: devops@aviladevops.com.br
- Slack: #saas-monitoring

## 📄 License

This monitoring stack configuration is part of the Ávila DevOps SaaS platform.
