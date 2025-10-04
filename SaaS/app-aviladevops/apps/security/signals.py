# Signals for security app
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_login_failed
import logging

logger = logging.getLogger('security')

@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    """Log tentativas de login falhadas"""
    username = credentials.get('username', 'unknown')
    client_ip = request.META.get('REMOTE_ADDR', 'unknown')

    logger.warning(f"Failed login attempt - Username: {username}, IP: {client_ip}")

@receiver(user_logged_in)
def log_successful_login(sender, user, request, **kwargs):
    """Log logins bem-sucedidos"""
    client_ip = request.META.get('REMOTE_ADDR', 'unknown')

    logger.info(f"Successful login - User: {user.username}, IP: {client_ip}")
