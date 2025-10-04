"""
Sistema de Monitoramento e Health Checks Avançado
Monitora saúde da aplicação, performance e disponibilidade
"""

import time
import psutil
import logging
from django.http import JsonResponse, HttpResponse
from django.core.cache import cache
from django.db import connection
from django.conf import settings
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class HealthCheckService:
    """Serviço de verificação de saúde"""

    @staticmethod
    def check_database():
        """Verifica conexão com banco de dados"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return {
                    'status': 'healthy' if result[0] == 1 else 'unhealthy',
                    'response_time_ms': 0,  # Medido externamente
                    'details': 'Database connection successful'
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'response_time_ms': 0,
                'details': f'Database error: {str(e)}'
            }

    @staticmethod
    def check_cache():
        """Verifica conexão com cache (Redis)"""
        try:
            start_time = time.time()
            test_key = 'health_check_test'
            test_value = str(timezone.now())

            cache.set(test_key, test_value, 30)
            retrieved_value = cache.get(test_key)
            cache.delete(test_key)

            response_time = (time.time() - start_time) * 1000

            if retrieved_value == test_value:
                return {
                    'status': 'healthy',
                    'response_time_ms': round(response_time, 2),
                    'details': 'Cache read/write successful'
                }
            else:
                return {
                    'status': 'unhealthy',
                    'response_time_ms': round(response_time, 2),
                    'details': 'Cache value mismatch'
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'response_time_ms': 0,
                'details': f'Cache error: {str(e)}'
            }

    @staticmethod
    def check_disk_space():
        """Verifica espaço em disco"""
        try:
            disk_usage = psutil.disk_usage('/')
            free_percent = (disk_usage.free / disk_usage.total) * 100

            if free_percent > 20:
                status = 'healthy'
            elif free_percent > 10:
                status = 'warning'
            else:
                status = 'critical'

            return {
                'status': status,
                'free_space_gb': round(disk_usage.free / (1024**3), 2),
                'total_space_gb': round(disk_usage.total / (1024**3), 2),
                'free_percent': round(free_percent, 2),
                'details': f'{free_percent:.1f}% disk space available'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'details': f'Disk check error: {str(e)}'
            }

    @staticmethod
    def check_memory():
        """Verifica uso de memória"""
        try:
            memory = psutil.virtual_memory()

            if memory.percent < 80:
                status = 'healthy'
            elif memory.percent < 90:
                status = 'warning'
            else:
                status = 'critical'

            return {
                'status': status,
                'used_percent': memory.percent,
                'available_gb': round(memory.available / (1024**3), 2),
                'total_gb': round(memory.total / (1024**3), 2),
                'details': f'{memory.percent:.1f}% memory used'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'details': f'Memory check error: {str(e)}'
            }

    @staticmethod
    def check_application_metrics():
        """Verifica métricas específicas da aplicação"""
        try:
            from .models import Agendamento, Cliente, Servico

            # Contadores básicos
            total_agendamentos = Agendamento.objects.count()
            total_clientes = Cliente.objects.filter(ativo=True).count()
            total_servicos = Servico.objects.filter(ativo=True).count()

            # Agendamentos hoje
            hoje = timezone.now().date()
            agendamentos_hoje = Agendamento.objects.filter(
                horario__date=hoje
            ).count()

            # Verificar se há dados mínimos
            if total_agendamentos == 0 and total_clientes == 0:
                status = 'warning'
                details = 'No data found in application'
            else:
                status = 'healthy'
                details = 'Application data available'

            return {
                'status': status,
                'total_agendamentos': total_agendamentos,
                'total_clientes': total_clientes,
                'total_servicos': total_servicos,
                'agendamentos_hoje': agendamentos_hoje,
                'details': details
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'details': f'Application metrics error: {str(e)}'
            }


@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """Endpoint de health check básico"""
    return JsonResponse({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'service': 'clinica-agendamentos'
    })


@csrf_exempt
@require_http_methods(["GET"])
def health_detailed(request):
    """Endpoint de health check detalhado"""
    start_time = time.time()

    checks = {}
    overall_status = 'healthy'

    # Database check
    db_start = time.time()
    checks['database'] = HealthCheckService.check_database()
    checks['database']['response_time_ms'] = round((time.time() - db_start) * 1000, 2)

    # Cache check
    checks['cache'] = HealthCheckService.check_cache()

    # System checks
    checks['disk'] = HealthCheckService.check_disk_space()
    checks['memory'] = HealthCheckService.check_memory()

    # Application checks
    checks['application'] = HealthCheckService.check_application_metrics()

    # Determinar status geral
    for check_name, check_result in checks.items():
        if check_result['status'] in ['unhealthy', 'critical']:
            overall_status = 'unhealthy'
            break
        elif check_result['status'] == 'warning' and overall_status == 'healthy':
            overall_status = 'warning'

    response_data = {
        'status': overall_status,
        'timestamp': timezone.now().isoformat(),
        'response_time_ms': round((time.time() - start_time) * 1000, 2),
        'service': 'clinica-agendamentos',
        'version': getattr(settings, 'VERSION', '1.0.0'),
        'checks': checks
    }

    # Status HTTP baseado na saúde
    status_code = 200 if overall_status == 'healthy' else 503

    return JsonResponse(response_data, status=status_code)


@api_view(['GET'])
@permission_classes([AllowAny])
def metrics(request):
    """Endpoint de métricas para Prometheus"""
    try:
        from .models import Agendamento, Cliente, Servico

        # Métricas de contadores
        metrics_data = []

        # Contadores totais
        metrics_data.append(f"agendamentos_total {Agendamento.objects.count()}")
        metrics_data.append(f"clientes_ativos_total {Cliente.objects.filter(ativo=True).count()}")
        metrics_data.append(f"servicos_ativos_total {Servico.objects.filter(ativo=True).count()}")

        # Agendamentos por status
        for status_info in Agendamento.objects.values('status').annotate(count=models.Count('id')):
            status = status_info['status']
            count = status_info['count']
            metrics_data.append(f'agendamentos_por_status{{status="{status}"}} {count}')

        # Agendamentos hoje
        hoje = timezone.now().date()
        agendamentos_hoje = Agendamento.objects.filter(horario__date=hoje).count()
        metrics_data.append(f"agendamentos_hoje {agendamentos_hoje}")

        # Métricas de sistema
        memory = psutil.virtual_memory()
        metrics_data.append(f"memory_usage_percent {memory.percent}")

        disk = psutil.disk_usage('/')
        disk_usage_percent = ((disk.total - disk.free) / disk.total) * 100
        metrics_data.append(f"disk_usage_percent {disk_usage_percent}")

        cpu_percent = psutil.cpu_percent(interval=1)
        metrics_data.append(f"cpu_usage_percent {cpu_percent}")

        # Timestamp da última atualização
        metrics_data.append(f"metrics_last_updated {int(time.time())}")

        # Retornar no formato Prometheus
        response_text = "\n".join(metrics_data)
        return HttpResponse(response_text, content_type='text/plain')

    except Exception as e:
        logger.error(f"Erro ao gerar métricas: {e}")
        return HttpResponse(f"# Error generating metrics: {str(e)}",
                          content_type='text/plain', status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def performance_metrics(request):
    """Métricas de performance detalhadas"""
    try:
        from django.db import connection
        from .models import Agendamento

        start_time = time.time()

        # Teste de performance do banco
        db_start = time.time()
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM agendamentos_agendamento")
            total_agendamentos = cursor.fetchone()[0]
        db_time = (time.time() - db_start) * 1000

        # Teste de performance do cache
        cache_start = time.time()
        cache.set('perf_test', 'test_value', 60)
        cache.get('perf_test')
        cache_time = (time.time() - cache_start) * 1000

        # Métricas de queries
        queries_count = len(connection.queries)

        total_time = (time.time() - start_time) * 1000

        return Response({
            'timestamp': timezone.now().isoformat(),
            'performance': {
                'total_response_time_ms': round(total_time, 2),
                'database_query_time_ms': round(db_time, 2),
                'cache_operation_time_ms': round(cache_time, 2),
                'queries_executed': queries_count,
                'total_agendamentos': total_agendamentos
            },
            'system': {
                'cpu_percent': psutil.cpu_percent(interval=0.1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage_percent': round(
                    (psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100, 2
                )
            }
        })

    except Exception as e:
        logger.error(f"Erro ao gerar métricas de performance: {e}")
        return Response({
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=500)


class PerformanceMonitoringMiddleware:
    """Middleware para monitoramento de performance"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        response = self.get_response(request)

        duration = time.time() - start_time

        # Log requisições lentas (> 1 segundo)
        if duration > 1.0:
            logger.warning(
                f"Slow request: {request.method} {request.path} - {duration:.2f}s"
            )

        # Adicionar header de tempo de resposta
        response['X-Response-Time'] = f"{duration:.3f}s"

        # Métricas para Prometheus (se configurado)
        if hasattr(settings, 'PROMETHEUS_METRICS') and settings.PROMETHEUS_METRICS:
            try:
                from prometheus_client import Histogram, Counter

                # Histogram de tempo de resposta
                REQUEST_TIME = Histogram('django_request_duration_seconds',
                                       'Time spent processing request',
                                       ['method', 'endpoint'])
                REQUEST_TIME.labels(method=request.method,
                                  endpoint=request.path).observe(duration)

                # Contador de requests
                REQUEST_COUNT = Counter('django_requests_total',
                                      'Total requests',
                                      ['method', 'endpoint', 'status'])
                REQUEST_COUNT.labels(method=request.method,
                                   endpoint=request.path,
                                   status=response.status_code).inc()

            except ImportError:
                pass  # prometheus_client não instalado

        return response


# Comando de management para verificar saúde
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Executa verificação de saúde da aplicação'

    def handle(self, *args, **options):
        self.stdout.write('Executando verificação de saúde...')

        checks = {
            'Database': HealthCheckService.check_database(),
            'Cache': HealthCheckService.check_cache(),
            'Disk': HealthCheckService.check_disk_space(),
            'Memory': HealthCheckService.check_memory(),
            'Application': HealthCheckService.check_application_metrics()
        }

        all_healthy = True

        for check_name, result in checks.items():
            status = result['status']
            if status == 'healthy':
                self.stdout.write(
                    self.style.SUCCESS(f'✓ {check_name}: {result.get("details", "OK")}')
                )
            elif status == 'warning':
                self.stdout.write(
                    self.style.WARNING(f'⚠ {check_name}: {result.get("details", "Warning")}')
                )
                all_healthy = False
            else:
                self.stdout.write(
                    self.style.ERROR(f'✗ {check_name}: {result.get("details", "Error")}')
                )
                all_healthy = False

        if all_healthy:
            self.stdout.write(self.style.SUCCESS('\n✓ Todos os sistemas estão saudáveis'))
            return 0
        else:
            self.stdout.write(self.style.ERROR('\n✗ Alguns sistemas apresentam problemas'))
            return 1
