"""
Signals de Segurança
Monitora eventos de segurança e toma ações preventivas
"""

import logging
from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.cache import cache
from .throttling import BruteForceProtection, get_client_ip

logger = logging.getLogger('security')


@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    """Log tentativas de login falhadas"""
    
    client_ip = get_client_ip(request)
    username = credentials.get('username', 'unknown')
    
    # Registrar tentativa falhada
    BruteForceProtection.record_failed_attempt(client_ip)
    
    # Log detalhado
    logger.warning(
        f"Failed login attempt | "
        f"Username: {username} | "
        f"IP: {client_ip} | "
        f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')}"
    )
    
    # Verificar se é um ataque coordenado
    failed_attempts = cache.get(f'failed_login_{client_ip}', 0)
    if failed_attempts > 5:
        logger.critical(
            f"Possible brute force attack detected | "
            f"IP: {client_ip} | "
            f"Failed attempts: {failed_attempts}"
        )


@receiver(user_logged_in)
def log_successful_login(sender, user, request, **kwargs):
    """Log logins bem-sucedidos e limpar tentativas falhadas"""
    
    client_ip = get_client_ip(request)
    
    # Limpar tentativas falhadas após login bem-sucedido
    BruteForceProtection.clear_failed_attempts(client_ip)
    
    # Log do login bem-sucedido
    logger.info(
        f"Successful login | "
        f"User: {user.username} (ID: {user.id}) | "
        f"IP: {client_ip} | "
        f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')}"
    )
    
    # Atualizar último login do usuário
    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])


@receiver(post_save, sender=User)
def log_user_creation(sender, instance, created, **kwargs):
    """Log criação de novos usuários"""
    
    if created:
        logger.info(
            f"New user created | "
            f"Username: {instance.username} | "
            f"Email: {instance.email} | "
            f"ID: {instance.id}"
        )
        
        # Verificar se é um usuário suspeito (sem email, etc.)
        if not instance.email:
            logger.warning(
                f"User created without email | "
                f"Username: {instance.username} | "
                f"ID: {instance.id}"
            )


def detect_suspicious_activity(user, action, request=None):
    """Detectar atividade suspeita de usuários"""
    
    client_ip = get_client_ip(request) if request else 'unknown'
    
    # Verificar múltiplas ações em pouco tempo
    cache_key = f"user_actions_{user.id}"
    actions = cache.get(cache_key, [])
    
    # Adicionar ação atual
    from django.utils import timezone
    actions.append({
        'action': action,
        'timestamp': timezone.now().isoformat(),
        'ip': client_ip
    })
    
    # Manter apenas últimas 50 ações
    actions = actions[-50:]
    cache.set(cache_key, actions, 3600)  # 1 hora
    
    # Analisar padrões suspeitos
    recent_actions = [a for a in actions if 
                     (timezone.now() - timezone.fromisoformat(a['timestamp'])).seconds < 300]  # 5 minutos
    
    if len(recent_actions) > 20:  # Mais de 20 ações em 5 minutos
        logger.warning(
            f"Suspicious activity detected | "
            f"User: {user.username} (ID: {user.id}) | "
            f"Actions in 5min: {len(recent_actions)} | "
            f"Current IP: {client_ip}"
        )
        
        # Verificar se são de IPs diferentes (possível account takeover)
        ips = set(a['ip'] for a in recent_actions)
        if len(ips) > 3:
            logger.critical(
                f"Possible account takeover | "
                f"User: {user.username} (ID: {user.id}) | "
                f"Different IPs: {list(ips)}"
            )


# Decorator para monitorar ações sensíveis
def monitor_sensitive_action(action_name):
    """Decorator para monitorar ações sensíveis"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                detect_suspicious_activity(request.user, action_name, request)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator