# 🔧 Monitoring Integration Guide

This guide provides step-by-step instructions for integrating monitoring into each service of the Ávila DevOps SaaS platform.

## 📋 Table of Contents

1. [Django Applications](#django-applications)
2. [Next.js Applications](#nextjs-applications)
3. [Nginx Configuration](#nginx-configuration)
4. [Database Monitoring](#database-monitoring)
5. [Celery Monitoring](#celery-monitoring)
6. [Custom Metrics](#custom-metrics)
7. [Testing](#testing)

## 🐍 Django Applications

### Installation

Add to `requirements.txt`:
```
prometheus-client==0.19.0
django-prometheus==2.3.1
```

Install:
```bash
pip install -r requirements.txt
```

### Configuration

1. **Update `settings.py`:**

```python
# Add to INSTALLED_APPS
INSTALLED_APPS = [
    'django_prometheus',  # Add at the beginning
    'django.contrib.admin',
    # ... other apps
]

# Add middleware (order matters!)
MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',  # First
    'django.middleware.security.SecurityMiddleware',
    # ... other middleware
    'django_prometheus.middleware.PrometheusAfterMiddleware',  # Last
]

# Optional: Configure service name
SERVICE_NAME = 'landing-page'  # or 'fiscal-system', 'main-app', etc.
VERSION = '1.0.0'
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')
```

2. **Update main `urls.py`:**

```python
from django.contrib import admin
from django.urls import path, include

# Import health check functions
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../monitoring'))
from django_health import health_check, ready_check, live_check

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Prometheus metrics endpoint
    path('', include('django_prometheus.urls')),
    
    # Health check endpoints
    path('health/', health_check, name='health'),
    path('health/ready/', ready_check, name='ready'),
    path('health/live/', live_check, name='live'),
    
    # Your other URLs
    # ...
]
```

3. **Add monitoring utilities to your project:**

Copy `monitoring/django_health.py` to your Django project:
```bash
cp monitoring/django_health.py LANDING-PAGE/monitoring.py
```

Or create a symbolic link:
```bash
ln -s ../../monitoring/django_health.py LANDING-PAGE/monitoring.py
```

### Using Custom Metrics

```python
from monitoring import (
    record_user_registration,
    record_user_login,
    set_active_users,
    record_payment_attempt,
    record_conversion
)

# In your views or signal handlers
def user_signup_view(request):
    # ... user registration logic
    
    # Record the registration
    tenant = request.tenant.slug if hasattr(request, 'tenant') else 'default'
    record_user_registration(tenant=tenant)
    
    return Response({'status': 'success'})

def user_login_view(request):
    # ... login logic
    
    tenant = get_tenant_from_request(request)
    record_user_login(tenant=tenant)
    
    return Response({'status': 'success'})

# Update active users count periodically (e.g., in a Celery task)
@periodic_task(run_every=timedelta(minutes=5))
def update_active_users():
    from django.contrib.sessions.models import Session
    from django.utils import timezone
    
    active_count = Session.objects.filter(
        expire_date__gte=timezone.now()
    ).count()
    
    set_active_users(active_count)
```

### Database Monitoring

Use `django-prometheus` database backend wrappers in `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django_prometheus.db.backends.postgresql',  # Instead of django.db.backends.postgresql
        'NAME': 'aviladevops_saas',
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Optional: Add connection pooling
DATABASES['default']['CONN_MAX_AGE'] = 600
```

### Cache Monitoring

Use `django-prometheus` cache backend wrappers:

```python
CACHES = {
    'default': {
        'BACKEND': 'django_prometheus.cache.backends.redis.RedisCache',  # Instead of django.core.cache.backends.redis.RedisCache
        'LOCATION': os.environ.get('REDIS_URL', 'redis://redis:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

## ⚛️ Next.js Applications

### Installation

```bash
cd clinica
npm install prom-client
```

### Configuration

1. **Copy monitoring utilities:**

```bash
cp monitoring/nextjs_health.ts clinica/lib/monitoring.ts
```

2. **Create health check endpoints:**

Create `pages/api/health.ts`:
```typescript
import { healthCheck } from '@/lib/monitoring';
export default healthCheck;
```

Create `pages/api/health/ready.ts`:
```typescript
import { readyCheck } from '@/lib/monitoring';
export default readyCheck;
```

Create `pages/api/health/live.ts`:
```typescript
import { liveCheck } from '@/lib/monitoring';
export default liveCheck;
```

3. **Create metrics endpoint:**

Create `pages/api/metrics.ts`:
```typescript
import { metricsHandler } from '@/lib/monitoring';
export default metricsHandler;
```

4. **Add request tracking middleware:**

Update `pages/_app.tsx`:
```typescript
import type { AppProps } from 'next/app';
import { useRouter } from 'next/router';
import { useEffect } from 'react';
import { metrics } from '@/lib/monitoring';

function MyApp({ Component, pageProps }: AppProps) {
  const router = useRouter();
  
  useEffect(() => {
    const handleRouteChange = (url: string) => {
      // Track page views
      if (typeof window !== 'undefined') {
        metrics.recordVisit?.();
      }
    };
    
    router.events.on('routeChangeComplete', handleRouteChange);
    
    return () => {
      router.events.off('routeChangeComplete', handleRouteChange);
    };
  }, [router.events]);
  
  return <Component {...pageProps} />;
}

export default MyApp;
```

5. **Wrap API routes with metrics:**

```typescript
import { withMetrics, metrics } from '@/lib/monitoring';

async function handler(req, res) {
  try {
    // Your API logic
    const result = await processRequest(req);
    
    // Record business metrics
    if (req.body.type === 'appointment') {
      metrics.recordAppointment('scheduled');
    }
    
    res.status(200).json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}

export default withMetrics(handler);
```

## 🌐 Nginx Configuration

Add Prometheus metrics module to nginx:

1. **Update `nginx/saas.conf`:**

```nginx
# Enable stub_status for metrics
server {
    listen 80;
    
    # Metrics endpoint (internal only)
    location /stub_status {
        stub_status on;
        access_log off;
        allow 172.16.0.0/12;  # Docker network
        deny all;
    }
    
    # Your other locations
    location / {
        # ...
    }
}
```

2. **Add custom log format for better parsing:**

```nginx
http {
    log_format json_combined escape=json
    '{'
        '"time_local":"$time_local",'
        '"remote_addr":"$remote_addr",'
        '"request_method":"$request_method",'
        '"request_uri":"$request_uri",'
        '"status": $status,'
        '"body_bytes_sent":$body_bytes_sent,'
        '"request_time":$request_time,'
        '"upstream_response_time":"$upstream_response_time",'
        '"http_referrer":"$http_referer",'
        '"http_user_agent":"$http_user_agent"'
    '}';
    
    access_log /var/log/nginx/access.log json_combined;
}
```

## 🗄️ Database Monitoring

### PostgreSQL

The `postgres-exporter` service is already configured in `docker-compose.monitoring.yml`.

To enable custom query metrics, create `monitoring/postgres_queries.yml`:

```yaml
pg_stat_user_tables:
  query: "SELECT schemaname, relname, seq_scan, seq_tup_read, idx_scan, idx_tup_fetch, n_tup_ins, n_tup_upd, n_tup_del FROM pg_stat_user_tables"
  metrics:
    - schemaname:
        usage: "LABEL"
        description: "Schema name"
    - relname:
        usage: "LABEL"
        description: "Table name"
    - seq_scan:
        usage: "COUNTER"
        description: "Number of sequential scans"
    - idx_scan:
        usage: "COUNTER"
        description: "Number of index scans"
```

### Redis

The `redis-exporter` is already configured. No additional setup needed.

## 🔄 Celery Monitoring

### Install Celery exporters

Add to `requirements.txt`:
```
celery-prometheus-exporter==1.10.0
```

### Configure Celery

Update your Celery configuration:

```python
# celery.py
from celery import Celery
from celery.signals import task_prerun, task_postrun, task_failure
from prometheus_client import Counter, Histogram
import time

app = Celery('saas')

# Celery metrics
celery_task_duration = Histogram(
    'celery_task_duration_seconds',
    'Duration of Celery tasks',
    ['task']
)

celery_task_total = Counter(
    'celery_task_total',
    'Total Celery tasks',
    ['task', 'status']
)

@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, **kwargs):
    task.start_time = time.time()

@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, **kwargs):
    if hasattr(task, 'start_time'):
        duration = time.time() - task.start_time
        celery_task_duration.labels(task=sender.name).observe(duration)
    celery_task_total.labels(task=sender.name, status='success').inc()

@task_failure.connect
def task_failure_handler(sender=None, task_id=None, **kwargs):
    celery_task_total.labels(task=sender.name, status='failure').inc()
```

## 📊 Custom Metrics Best Practices

### Naming Conventions

Follow Prometheus naming conventions:
- Use `_total` suffix for counters
- Use `_seconds` suffix for durations
- Use lowercase with underscores
- Include unit in the name

Good examples:
```python
saas_user_registrations_total
saas_payment_processing_duration_seconds
saas_active_sessions_count
```

### Label Best Practices

- Keep cardinality low (< 100 unique values per label)
- Don't use user IDs or timestamps as labels
- Use labels for dimensions you want to aggregate by

Good:
```python
requests_total{service="landing-page", status="200"}
```

Bad:
```python
requests_total{user_id="12345", timestamp="2024-01-01"}  # Too high cardinality
```

### Example: Complete View Instrumentation

```python
from django.views import View
from prometheus_client import Counter, Histogram
import time

# Define metrics
view_requests = Counter(
    'view_requests_total',
    'Total view requests',
    ['view', 'method', 'status']
)

view_duration = Histogram(
    'view_duration_seconds',
    'View duration',
    ['view', 'method']
)

class MonitoredView(View):
    def dispatch(self, request, *args, **kwargs):
        start_time = time.time()
        view_name = self.__class__.__name__
        method = request.method
        
        try:
            response = super().dispatch(request, *args, **kwargs)
            status = response.status_code
            
            # Record metrics
            view_requests.labels(
                view=view_name,
                method=method,
                status=status
            ).inc()
            
            duration = time.time() - start_time
            view_duration.labels(
                view=view_name,
                method=method
            ).observe(duration)
            
            return response
            
        except Exception as e:
            view_requests.labels(
                view=view_name,
                method=method,
                status=500
            ).inc()
            raise
```

## 🧪 Testing

### Test Health Endpoints

```bash
# Django applications
curl http://localhost:8000/health/
curl http://localhost:8000/health/ready/
curl http://localhost:8000/health/live/
curl http://localhost:8000/metrics

# Next.js applications
curl http://localhost:3000/api/health
curl http://localhost:3000/api/health/ready
curl http://localhost:3000/api/health/live
curl http://localhost:3000/api/metrics
```

### Verify Prometheus Scraping

1. Start monitoring stack:
```bash
docker-compose -f docker-compose.monitoring.yml up -d
```

2. Check Prometheus targets:
```
http://localhost:9090/targets
```

3. Query metrics:
```
http://localhost:9090/graph
```

Example queries:
```promql
# Request rate
rate(django_http_requests_total[5m])

# Error rate
rate(django_http_responses_total_by_status_total{status=~"5.."}[5m])

# 95th percentile latency
histogram_quantile(0.95, rate(django_http_request_duration_seconds_bucket[5m]))
```

### Test Grafana Dashboards

1. Access Grafana: http://localhost:3001
2. Login with admin/admin
3. Navigate to Dashboards → Ávila DevOps SaaS
4. Verify data is showing in all panels

## 📝 Checklist

### For Each Django Service

- [ ] Install `django-prometheus` and `prometheus-client`
- [ ] Add to `INSTALLED_APPS`
- [ ] Add middleware
- [ ] Add health check endpoints to URLs
- [ ] Update database backend to monitored version
- [ ] Update cache backend to monitored version
- [ ] Add custom business metrics
- [ ] Test health endpoints
- [ ] Verify metrics in Prometheus

### For Each Next.js Service

- [ ] Install `prom-client`
- [ ] Copy monitoring utilities
- [ ] Create health check endpoints
- [ ] Create metrics endpoint
- [ ] Add request tracking
- [ ] Add business metrics
- [ ] Test endpoints
- [ ] Verify metrics in Prometheus

### Infrastructure

- [ ] Configure Nginx with stub_status
- [ ] Set up PostgreSQL exporter
- [ ] Set up Redis exporter
- [ ] Configure Celery metrics
- [ ] Add custom application metrics
- [ ] Test all exporters
- [ ] Verify dashboards

## 🆘 Troubleshooting

### Metrics Not Showing

1. Check if service is running:
```bash
docker-compose -f docker-compose.monitoring.yml ps
```

2. Check Prometheus targets:
```
http://localhost:9090/targets
```

3. Test metric endpoint directly:
```bash
curl http://localhost:8000/metrics
```

4. Check Prometheus logs:
```bash
docker-compose -f docker-compose.monitoring.yml logs prometheus
```

### Health Check Failing

1. Check application logs
2. Test database connection manually
3. Test cache connection manually
4. Verify environment variables

### Dashboard Not Loading

1. Verify Prometheus data source in Grafana
2. Check if metrics exist in Prometheus
3. Verify time range selection
4. Check dashboard JSON for errors

## 📚 Additional Resources

- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [Django Prometheus](https://github.com/korfuri/django-prometheus)
- [Prom Client (Node.js)](https://github.com/siimon/prom-client)
- [Grafana Dashboards](https://grafana.com/grafana/dashboards/)

## 🤝 Support

For questions or issues:
- Create an issue in the repository
- Contact: devops@aviladevops.com.br
- Slack: #saas-monitoring
