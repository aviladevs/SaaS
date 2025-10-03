from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Modelo de usuário personalizado"""

    # Campos básicos
    phone = models.CharField(_('Telefone'), max_length=20, blank=True)
    company = models.CharField(_('Empresa'), max_length=100, blank=True)
    position = models.CharField(_('Cargo'), max_length=50, blank=True)
    bio = models.TextField(_('Bio'), blank=True, max_length=500)

    # Campos de endereço
    address = models.CharField(_('Endereço'), max_length=200, blank=True)
    city = models.CharField(_('Cidade'), max_length=50, blank=True)
    state = models.CharField(_('Estado'), max_length=2, blank=True)
    zip_code = models.CharField(_('CEP'), max_length=10, blank=True)
    country = models.CharField(_('País'), max_length=50, default='Brasil')

    # Campos de configuração
    avatar = models.ImageField(_('Avatar'), upload_to='avatars/', blank=True, null=True)
    website = models.URLField(_('Website'), blank=True)
    linkedin = models.URLField(_('LinkedIn'), blank=True)
    github = models.URLField(_('GitHub'), blank=True)

    # Campos de status
    is_verified = models.BooleanField(_('Verificado'), default=False)
    verification_token = models.CharField(_('Token de verificação'), max_length=100, blank=True)

    # Campos de timestamps
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)
    last_login_ip = models.GenericIPAddressField(_('Último IP de login'), blank=True, null=True)

    # Campos de preferências
    newsletter_subscribed = models.BooleanField(_('Inscrito na newsletter'), default=True)
    marketing_emails = models.BooleanField(_('Emails de marketing'), default=True)
    language = models.CharField(_('Idioma'), max_length=10, default='pt-br')
    timezone = models.CharField(_('Fuso horário'), max_length=50, default='America/Sao_Paulo')

    class Meta:
        verbose_name = _('Usuário')
        verbose_name_plural = _('Usuários')
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"

    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower()
        super().save(*args, **kwargs)
