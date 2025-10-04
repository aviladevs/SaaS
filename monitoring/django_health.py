"""
Health Check and Monitoring Utilities for Django Applications
Provides reusable health check endpoints and Prometheus metrics integration

Installation:
1. Install required packages:
   pip install prometheus-client django-prometheus

2. Add to INSTALLED_APPS in settings.py:
   INSTALLED_APPS = [
       'django_prometheus',
       ...
   ]

3. Add middleware in settings.py (at the beginning and end):
   MIDDLEWARE = [
       'django_prometheus.middleware.PrometheusBeforeMiddleware',
       ...
       'django_prometheus.middleware.PrometheusAfterMiddleware',
   ]

4. Include in your main urls.py:
   from django.urls import path, include
   from monitoring.health import health_check, ready_check, live_check
   
   urlpatterns = [
       path('', include('django_prometheus.urls')),
       path('health/', health_check, name='health'),
       path('health/ready/', ready_check, name='ready'),
       path('health/live/', live_check, name='live'),
       ...
   ]
"""

from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.conf import settings
import time
import os

# Custom metrics (optional - requires prometheus_client)
try:
    from prometheus_client import Counter, Gauge, Histogram
    
    # Business metrics
    user_registrations = Counter(
        'saas_user_registrations_total',
        'Total number of user registrations',
        ['tenant']
    )
    
    user_logins = Counter(
        'saas_user_logins_total',
        'Total number of user logins',
        ['tenant']
    )
    
    active_users = Gauge(
        'saas_active_users_total',
        'Number of currently active users',
        ['tenant']
    )
    
    # Transaction metrics
    payment_attempts = Counter(
        'saas_payment_attempts_total',
        'Total payment attempts',
        ['tenant', 'status']
    )
    
    payment_successful = Counter(
        'saas_payment_successful_total',
        'Total successful payments',
        ['tenant']
    )
    
    payment_failures = Counter(
        'saas_payment_failures_total',
        'Total failed payments',
        ['tenant', 'reason']
    )
    
    # Revenue metrics
    revenue_total = Gauge(
        'saas_revenue_total',
        'Total revenue',
        ['tenant', 'currency']
    )
    
    subscription_revenue = Gauge(
        'saas_subscription_revenue_monthly',
        'Monthly subscription revenue (MRR)',
        ['tenant', 'currency']
    )
    
    # User behavior metrics
    conversions = Counter(
        'saas_conversions_total',
        'Total conversions',
        ['tenant', 'type']
    )
    
    visits = Counter(
        'saas_visits_total',
        'Total site visits',
        ['tenant']
    )
    
    user_cancellations = Counter(
        'saas_user_cancellations_total',
        'Total user cancellations',
        ['tenant', 'reason']
    )
    
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False


def check_database():
    """Check database connectivity"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return True, "Database connection OK"
    except Exception as e:
        return False, f"Database error: {str(e)}"


def check_cache():
    """Check cache connectivity"""
    try:
        cache.set('health_check', 'ok', 10)
        value = cache.get('health_check')
        if value == 'ok':
            return True, "Cache connection OK"
        return False, "Cache read/write failed"
    except Exception as e:
        return False, f"Cache error: {str(e)}"


def check_disk_space():
    """Check disk space availability"""
    try:
        stat = os.statvfs('/')
        available_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
        total_gb = (stat.f_blocks * stat.f_frsize) / (1024**3)
        usage_percent = ((total_gb - available_gb) / total_gb) * 100
        
        if usage_percent > 95:
            return False, f"Disk usage critical: {usage_percent:.1f}%"
        elif usage_percent > 85:
            return True, f"Disk usage warning: {usage_percent:.1f}%"
        return True, f"Disk usage OK: {usage_percent:.1f}%"
    except Exception as e:
        return False, f"Disk check error: {str(e)}"


def health_check(request):
    """
    Complete health check endpoint
    Returns JSON with detailed health information
    HTTP 200 if all checks pass, 503 if any check fails
    """
    start_time = time.time()
    
    checks = {
        'database': check_database(),
        'cache': check_cache(),
        'disk': check_disk_space(),
    }
    
    # Determine overall status
    all_healthy = all(status for status, _ in checks.values())
    
    response_data = {
        'status': 'healthy' if all_healthy else 'unhealthy',
        'timestamp': time.time(),
        'service': os.environ.get('SERVICE_NAME', 'unknown'),
        'version': getattr(settings, 'VERSION', '1.0.0'),
        'environment': getattr(settings, 'ENVIRONMENT', 'development'),
        'checks': {
            name: {
                'status': 'pass' if status else 'fail',
                'message': message
            }
            for name, (status, message) in checks.items()
        },
        'response_time_ms': (time.time() - start_time) * 1000
    }
    
    status_code = 200 if all_healthy else 503
    return JsonResponse(response_data, status=status_code)


def ready_check(request):
    """
    Readiness probe for Kubernetes
    Returns 200 when the service is ready to accept traffic
    """
    db_ok, _ = check_database()
    cache_ok, _ = check_cache()
    
    if db_ok and cache_ok:
        return JsonResponse({
            'status': 'ready',
            'timestamp': time.time()
        })
    
    return JsonResponse({
        'status': 'not_ready',
        'timestamp': time.time()
    }, status=503)


def live_check(request):
    """
    Liveness probe for Kubernetes
    Returns 200 when the service is alive (even if not ready)
    Only checks if the application can respond
    """
    return JsonResponse({
        'status': 'alive',
        'timestamp': time.time()
    })


# Metric helper functions (only available if prometheus_client is installed)
if METRICS_AVAILABLE:
    def record_user_registration(tenant='default'):
        """Record a user registration"""
        user_registrations.labels(tenant=tenant).inc()
    
    def record_user_login(tenant='default'):
        """Record a user login"""
        user_logins.labels(tenant=tenant).inc()
    
    def set_active_users(count, tenant='default'):
        """Set the number of active users"""
        active_users.labels(tenant=tenant).set(count)
    
    def record_payment_attempt(status, tenant='default'):
        """Record a payment attempt"""
        payment_attempts.labels(tenant=tenant, status=status).inc()
        
        if status == 'success':
            payment_successful.labels(tenant=tenant).inc()
    
    def record_payment_failure(reason, tenant='default'):
        """Record a payment failure"""
        payment_failures.labels(tenant=tenant, reason=reason).inc()
    
    def set_revenue(amount, tenant='default', currency='BRL'):
        """Set total revenue"""
        revenue_total.labels(tenant=tenant, currency=currency).set(amount)
    
    def set_mrr(amount, tenant='default', currency='BRL'):
        """Set monthly recurring revenue"""
        subscription_revenue.labels(tenant=tenant, currency=currency).set(amount)
    
    def record_conversion(conversion_type, tenant='default'):
        """Record a conversion"""
        conversions.labels(tenant=tenant, type=conversion_type).inc()
    
    def record_visit(tenant='default'):
        """Record a site visit"""
        visits.labels(tenant=tenant).inc()
    
    def record_cancellation(reason, tenant='default'):
        """Record a user cancellation"""
        user_cancellations.labels(tenant=tenant, reason=reason).inc()
else:
    # Stub functions if metrics not available
    def record_user_registration(tenant='default'): pass
    def record_user_login(tenant='default'): pass
    def set_active_users(count, tenant='default'): pass
    def record_payment_attempt(status, tenant='default'): pass
    def record_payment_failure(reason, tenant='default'): pass
    def set_revenue(amount, tenant='default', currency='BRL'): pass
    def set_mrr(amount, tenant='default', currency='BRL'): pass
    def record_conversion(conversion_type, tenant='default'): pass
    def record_visit(tenant='default'): pass
    def record_cancellation(reason, tenant='default'): pass
