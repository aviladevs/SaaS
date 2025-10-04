"""
Sistema de Rate Limiting Avançado
Implementação de throttling específico por endpoint e usuário
"""

from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.core.cache import cache
from django.http import HttpRequest
import time


class LoginRateThrottle(UserRateThrottle):
    """Rate limiting específico para login"""
    scope = 'login'
    rate = '5/min'  # 5 tentativas por minuto


class APIRateThrottle(UserRateThrottle):
    """Rate limiting para API geral"""
    scope = 'api'
    rate = '100/min'  # 100 requests por minuto


class AdminRateThrottle(UserRateThrottle):
    """Rate limiting para ações administrativas"""
    scope = 'admin'
    rate = '50/min'  # 50 ações por minuto


class CustomAnonRateThrottle(AnonRateThrottle):
    """Rate limiting para usuários anônimos"""
    scope = 'anon'
    rate = '20/min'  # 20 requests por minuto


class PasswordResetThrottle(AnonRateThrottle):
    """Rate limiting para reset de senha"""
    scope = 'password_reset'
    rate = '3/hour'  # 3 tentativas por hora

    def get_cache_key(self, request, view):
        """Cache key baseado no IP e email"""
        ident = self.get_ident(request)
        email = request.data.get('email', 'unknown')
        return f'password_reset_{ident}_{email}'


class BruteForceProtection:
    """Proteção contra ataques de força bruta"""

    @staticmethod
    def check_failed_attempts(ip_address: str, max_attempts: int = 10) -> bool:
        """Verifica tentativas de login falhadas"""
        cache_key = f'failed_login_{ip_address}'
        attempts = cache.get(cache_key, 0)
        return attempts < max_attempts

    @staticmethod
    def record_failed_attempt(ip_address: str, timeout: int = 3600):
        """Registra tentativa de login falhada"""
        cache_key = f'failed_login_{ip_address}'
        attempts = cache.get(cache_key, 0)
        cache.set(cache_key, attempts + 1, timeout)

    @staticmethod
    def clear_failed_attempts(ip_address: str):
        """Limpa tentativas após login bem-sucedido"""
        cache_key = f'failed_login_{ip_address}'
        cache.delete(cache_key)


def get_client_ip(request: HttpRequest) -> str:
    """Obter IP real do cliente considerando proxies"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
