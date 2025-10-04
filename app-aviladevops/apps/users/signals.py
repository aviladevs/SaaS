"""
Signals for user authentication system
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.users.models import User, AuditLog


@receiver(post_save, sender=User)
def log_user_creation(sender, instance, created, **kwargs):
    """Log when a user is created"""
    if created:
        AuditLog.objects.create(
            tenant=instance.tenant,
            user=instance,
            event='user_created',
            details={'username': instance.username, 'email': instance.email}
        )
