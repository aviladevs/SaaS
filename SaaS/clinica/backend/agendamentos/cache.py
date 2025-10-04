"""
Sistema de Cache Inteligente para Performance
Cache automatizado com invalidação inteligente
"""

from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from functools import wraps
from datetime import timedelta
import hashlib
import json


def cache_key_generator(*args, **kwargs):
    """Gera chave de cache baseada nos argumentos"""
    key_data = {
        'args': args,
        'kwargs': sorted(kwargs.items())
    }
    key_string = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_string.encode()).hexdigest()


def cache_result(timeout=3600, key_prefix=""):
    """Decorator para cachear resultados de funções"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Gerar chave de cache
            cache_key = f"{key_prefix}_{func.__name__}_{cache_key_generator(*args, **kwargs)}"

            # Tentar buscar no cache
            result = cache.get(cache_key)
            if result is not None:
                return result

            # Executar função e cachear resultado
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)

            return result
        return wrapper
    return decorator


class CacheService:
    """Serviço centralizado de cache"""

    # Prefixos de cache
    DASHBOARD_PREFIX = "dashboard"
    AGENDAMENTOS_PREFIX = "agendamentos"
    CLIENTES_PREFIX = "clientes"
    SERVICOS_PREFIX = "servicos"
    RELATORIOS_PREFIX = "relatorios"

    # Timeouts de cache (em segundos)
    CACHE_SHORT = 300      # 5 minutos
    CACHE_MEDIUM = 1800    # 30 minutos
    CACHE_LONG = 3600      # 1 hora
    CACHE_VERY_LONG = 86400  # 24 horas

    @classmethod
    def get_dashboard_data(cls, user_id=None):
        """Cache para dados do dashboard"""
        cache_key = f"{cls.DASHBOARD_PREFIX}_data_{user_id or 'all'}"

        data = cache.get(cache_key)
        if data is None:
            # Importar aqui para evitar import circular
            from .views import AgendamentoViewSet
            from rest_framework.request import Request
            from django.http import HttpRequest

            # Simular request para o dashboard
            request = Request(HttpRequest())
            viewset = AgendamentoViewSet()
            viewset.request = request

            response = viewset.dashboard(request)
            data = response.data

            cache.set(cache_key, data, cls.CACHE_MEDIUM)

        return data

    @classmethod
    def get_agendamentos_hoje(cls):
        """Cache para agendamentos de hoje"""
        from django.utils import timezone
        from .models import Agendamento

        cache_key = f"{cls.AGENDAMENTOS_PREFIX}_hoje_{timezone.now().date()}"

        agendamentos = cache.get(cache_key)
        if agendamentos is None:
            hoje = timezone.now().date()
            agendamentos = list(
                Agendamento.objects.filter(
                    horario__date=hoje
                ).select_related('cliente', 'servico').values(
                    'id', 'cliente__nome', 'servico__nome',
                    'horario', 'status', 'valor_cobrado'
                )
            )
            cache.set(cache_key, agendamentos, cls.CACHE_SHORT)

        return agendamentos

    @classmethod
    def get_servicos_ativos(cls):
        """Cache para serviços ativos"""
        cache_key = f"{cls.SERVICOS_PREFIX}_ativos"

        servicos = cache.get(cache_key)
        if servicos is None:
            from .models import Servico
            servicos = list(
                Servico.objects.filter(ativo=True).values(
                    'id', 'nome', 'valor', 'duracao_minutos', 'cor_calendario'
                )
            )
            cache.set(cache_key, servicos, cls.CACHE_LONG)

        return servicos

    @classmethod
    def get_estatisticas_mes(cls, mes=None, ano=None):
        """Cache para estatísticas mensais"""
        from django.utils import timezone

        if not mes or not ano:
            hoje = timezone.now()
            mes = hoje.month
            ano = hoje.year

        cache_key = f"{cls.RELATORIOS_PREFIX}_estatisticas_{ano}_{mes}"

        stats = cache.get(cache_key)
        if stats is None:
            from .models import Agendamento
            from django.db.models import Count, Sum

            # Calcular estatísticas
            agendamentos_mes = Agendamento.objects.filter(
                horario__year=ano,
                horario__month=mes
            )

            stats = {
                'total_agendamentos': agendamentos_mes.count(),
                'receita_total': agendamentos_mes.filter(
                    status='concluido'
                ).aggregate(
                    total=Sum('valor_cobrado')
                )['total'] or 0,
                'por_status': list(
                    agendamentos_mes.values('status').annotate(
                        count=Count('id')
                    )
                ),
                'por_servico': list(
                    agendamentos_mes.values(
                        'servico__nome'
                    ).annotate(
                        count=Count('id'),
                        receita=Sum('valor_cobrado')
                    ).order_by('-count')[:10]
                )
            }

            # Cache por mais tempo se for mês passado
            timeout = cls.CACHE_VERY_LONG if mes < timezone.now().month else cls.CACHE_MEDIUM
            cache.set(cache_key, stats, timeout)

        return stats

    @classmethod
    def invalidate_dashboard(cls):
        """Invalida cache do dashboard"""
        cache.delete_many([
            f"{cls.DASHBOARD_PREFIX}_data_all",
            f"{cls.DASHBOARD_PREFIX}_data_None"
        ])

    @classmethod
    def invalidate_agendamentos(cls):
        """Invalida cache de agendamentos"""
        from django.utils import timezone

        # Invalidar agendamentos de hoje
        hoje = timezone.now().date()
        cache.delete(f"{cls.AGENDAMENTOS_PREFIX}_hoje_{hoje}")

        # Invalidar dashboard
        cls.invalidate_dashboard()

    @classmethod
    def invalidate_servicos(cls):
        """Invalida cache de serviços"""
        cache.delete(f"{cls.SERVICOS_PREFIX}_ativos")
        cls.invalidate_dashboard()

    @classmethod
    def invalidate_estatisticas(cls, mes=None, ano=None):
        """Invalida cache de estatísticas"""
        from django.utils import timezone

        if not mes or not ano:
            hoje = timezone.now()
            mes = hoje.month
            ano = hoje.year

        cache.delete(f"{cls.RELATORIOS_PREFIX}_estatisticas_{ano}_{mes}")


# Signals para invalidação automática de cache
@receiver(post_save, sender='agendamentos.Agendamento')
@receiver(post_delete, sender='agendamentos.Agendamento')
def invalidate_agendamento_cache(sender, **kwargs):
    """Invalida cache quando agendamento é alterado"""
    CacheService.invalidate_agendamentos()


@receiver(post_save, sender='agendamentos.Cliente')
@receiver(post_delete, sender='agendamentos.Cliente')
def invalidate_cliente_cache(sender, **kwargs):
    """Invalida cache quando cliente é alterado"""
    CacheService.invalidate_dashboard()


@receiver(post_save, sender='agendamentos.Servico')
@receiver(post_delete, sender='agendamentos.Servico')
def invalidate_servico_cache(sender, **kwargs):
    """Invalida cache quando serviço é alterado"""
    CacheService.invalidate_servicos()


# Decorators de cache específicos
def cache_dashboard(timeout=CacheService.CACHE_MEDIUM):
    """Decorator específico para dashboard"""
    return cache_result(timeout=timeout, key_prefix=CacheService.DASHBOARD_PREFIX)


def cache_agendamentos(timeout=CacheService.CACHE_SHORT):
    """Decorator específico para agendamentos"""
    return cache_result(timeout=timeout, key_prefix=CacheService.AGENDAMENTOS_PREFIX)


def cache_relatorios(timeout=CacheService.CACHE_LONG):
    """Decorator específico para relatórios"""
    return cache_result(timeout=timeout, key_prefix=CacheService.RELATORIOS_PREFIX)


# Middleware de cache para templates
class TemplateCacheMiddleware:
    """Middleware para cache de templates"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Adicionar headers de cache para recursos estáticos
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            response['Cache-Control'] = 'public, max-age=86400'  # 24 horas

        return response


# Utilitários de cache
def warm_cache():
    """Aquece o cache com dados frequentemente acessados"""
    try:
        # Dashboard
        CacheService.get_dashboard_data()

        # Agendamentos de hoje
        CacheService.get_agendamentos_hoje()

        # Serviços ativos
        CacheService.get_servicos_ativos()

        # Estatísticas do mês atual
        CacheService.get_estatisticas_mes()

        return True
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erro ao aquecer cache: {e}")
        return False


def clear_all_cache():
    """Limpa todo o cache da aplicação"""
    cache.clear()
    return True


def get_cache_stats():
    """Retorna estatísticas do cache"""
    try:
        # Esta implementação depende do backend de cache usado
        # Para Redis, podemos usar redis.info()
        from django.core.cache.backends.redis import RedisCache

        if isinstance(cache, RedisCache):
            redis_client = cache._cache.get_client(write=True)
            info = redis_client.info()

            return {
                'used_memory': info.get('used_memory_human', 'N/A'),
                'connected_clients': info.get('connected_clients', 0),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'hit_rate': round(
                    info.get('keyspace_hits', 0) /
                    max(info.get('keyspace_hits', 0) + info.get('keyspace_misses', 0), 1) * 100,
                    2
                )
            }
        else:
            return {'message': 'Estatísticas não disponíveis para este backend de cache'}

    except Exception as e:
        return {'error': str(e)}
