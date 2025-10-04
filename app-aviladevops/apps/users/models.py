from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator
import uuid
import secrets


class Tenant(models.Model):
    """Modelo de Tenant para isolamento multi-tenant"""
    
    PLAN_CHOICES = [
        ('basic', 'Basic'),
        ('pro', 'Professional'),
        ('enterprise', 'Enterprise'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('trial', 'Trial'),
        ('inactive', 'Inactive'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('Nome'), max_length=100, unique=True)
    slug = models.SlugField(_('Slug'), max_length=100, unique=True)
    domain = models.CharField(_('Domínio'), max_length=255, unique=True)
    
    # Plan and status
    plan = models.CharField(_('Plano'), max_length=20, choices=PLAN_CHOICES, default='basic')
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='trial')
    
    # Limits based on plan
    max_users = models.IntegerField(_('Máximo de usuários'), default=10)
    storage_limit = models.IntegerField(_('Limite de armazenamento (GB)'), default=10)
    
    # Tenant owner
    owner_email = models.EmailField(_('Email do proprietário'))
    
    # Timestamps
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)
    trial_ends_at = models.DateTimeField(_('Trial termina em'), null=True, blank=True)
    
    # Settings (stored as JSON)
    settings = models.JSONField(_('Configurações'), default=dict, blank=True)
    
    class Meta:
        verbose_name = _('Tenant')
        verbose_name_plural = _('Tenants')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_user_count(self):
        """Retorna número de usuários ativos no tenant"""
        return self.users.filter(is_active=True).count()
    
    def is_within_user_limit(self):
        """Verifica se tenant está dentro do limite de usuários"""
        return self.get_user_count() < self.max_users


class Role(models.Model):
    """Modelo de Role para RBAC"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='roles')
    name = models.CharField(_('Nome'), max_length=50)
    description = models.TextField(_('Descrição'), blank=True)
    
    # System roles cannot be deleted
    is_system = models.BooleanField(_('Role do sistema'), default=False)
    
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)
    
    class Meta:
        verbose_name = _('Role')
        verbose_name_plural = _('Roles')
        unique_together = [['tenant', 'name']]
        ordering = ['tenant', 'name']
    
    def __str__(self):
        return f"{self.tenant.name} - {self.name}"


class Permission(models.Model):
    """Modelo de Permission para RBAC granular"""
    
    RESOURCE_CHOICES = [
        ('user', 'User Management'),
        ('tenant', 'Tenant Management'),
        ('service', 'Service Management'),
        ('project', 'Project Management'),
        ('blog', 'Blog Management'),
        ('contact', 'Contact Management'),
        ('analytics', 'Analytics'),
        ('settings', 'Settings'),
    ]
    
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('read', 'Read'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('list', 'List'),
        ('export', 'Export'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='permissions')
    resource = models.CharField(_('Recurso'), max_length=50, choices=RESOURCE_CHOICES)
    action = models.CharField(_('Ação'), max_length=20, choices=ACTION_CHOICES)
    
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Permissão')
        verbose_name_plural = _('Permissões')
        unique_together = [['role', 'resource', 'action']]
        ordering = ['role', 'resource', 'action']
    
    def __str__(self):
        return f"{self.role.name} - {self.action} {self.resource}"


class User(AbstractUser):
    """Modelo de usuário personalizado"""

    # Multi-tenant association
    tenant = models.ForeignKey(
        Tenant, 
        on_delete=models.CASCADE, 
        related_name='users',
        null=True,
        blank=True,
        verbose_name=_('Tenant')
    )
    roles = models.ManyToManyField(
        Role,
        related_name='users',
        blank=True,
        verbose_name=_('Roles')
    )

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
    
    def has_permission(self, resource, action):
        """Verifica se o usuário tem uma permissão específica"""
        if self.is_superuser:
            return True
        
        return Permission.objects.filter(
            role__in=self.roles.all(),
            resource=resource,
            action=action
        ).exists()


class OAuthProvider(models.Model):
    """Configuração de provedores OAuth por tenant"""
    
    PROVIDER_CHOICES = [
        ('google', 'Google Workspace'),
        ('microsoft', 'Microsoft Azure AD'),
        ('github', 'GitHub'),
        ('gitlab', 'GitLab'),
        ('saml', 'SAML 2.0'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='oauth_providers')
    provider = models.CharField(_('Provedor'), max_length=20, choices=PROVIDER_CHOICES)
    
    # OAuth credentials
    client_id = models.CharField(_('Client ID'), max_length=255)
    client_secret = models.CharField(_('Client Secret'), max_length=255)
    
    # SAML specific
    saml_metadata_url = models.URLField(_('SAML Metadata URL'), blank=True)
    
    # Settings
    enabled = models.BooleanField(_('Habilitado'), default=True)
    auto_create_users = models.BooleanField(_('Auto-criar usuários'), default=False)
    default_role = models.ForeignKey(
        Role, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='oauth_providers',
        verbose_name=_('Role padrão')
    )
    
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)
    
    class Meta:
        verbose_name = _('Provedor OAuth')
        verbose_name_plural = _('Provedores OAuth')
        unique_together = [['tenant', 'provider']]
        ordering = ['tenant', 'provider']
    
    def __str__(self):
        return f"{self.tenant.name} - {self.get_provider_display()}"


class TOTPDevice(models.Model):
    """Dispositivo TOTP para MFA"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='totp_devices')
    name = models.CharField(_('Nome do dispositivo'), max_length=100)
    secret = models.CharField(_('Segredo'), max_length=32)
    confirmed = models.BooleanField(_('Confirmado'), default=False)
    
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    last_used_at = models.DateTimeField(_('Último uso'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Dispositivo TOTP')
        verbose_name_plural = _('Dispositivos TOTP')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"


class BackupCode(models.Model):
    """Códigos de backup para MFA"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='backup_codes')
    code = models.CharField(_('Código'), max_length=12, unique=True)
    used = models.BooleanField(_('Usado'), default=False)
    used_at = models.DateTimeField(_('Usado em'), null=True, blank=True)
    
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Código de backup')
        verbose_name_plural = _('Códigos de backup')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.code[:4]}****"
    
    @staticmethod
    def generate_code():
        """Gera um código de backup aleatório"""
        return secrets.token_hex(6).upper()


class UserInvitation(models.Model):
    """Convites de usuários para tenants"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='invitations')
    email = models.EmailField(_('Email'))
    invited_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sent_invitations',
        verbose_name=_('Convidado por')
    )
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='invitations')
    
    token = models.CharField(_('Token'), max_length=64, unique=True)
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    expires_at = models.DateTimeField(_('Expira em'))
    accepted_at = models.DateTimeField(_('Aceito em'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Convite de usuário')
        verbose_name_plural = _('Convites de usuários')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.email} - {self.tenant.name}"
    
    @staticmethod
    def generate_token():
        """Gera token único para convite"""
        return secrets.token_urlsafe(48)


class AuditLog(models.Model):
    """Log de auditoria para eventos de autenticação"""
    
    EVENT_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('login_failed', 'Login Failed'),
        ('password_change', 'Password Change'),
        ('password_reset', 'Password Reset'),
        ('mfa_enabled', 'MFA Enabled'),
        ('mfa_disabled', 'MFA Disabled'),
        ('user_created', 'User Created'),
        ('user_updated', 'User Updated'),
        ('user_deleted', 'User Deleted'),
        ('role_assigned', 'Role Assigned'),
        ('role_removed', 'Role Removed'),
        ('invitation_sent', 'Invitation Sent'),
        ('invitation_accepted', 'Invitation Accepted'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        Tenant, 
        on_delete=models.CASCADE, 
        related_name='audit_logs',
        null=True,
        blank=True
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        related_name='audit_logs',
        null=True,
        blank=True
    )
    
    event = models.CharField(_('Evento'), max_length=50, choices=EVENT_CHOICES)
    ip_address = models.GenericIPAddressField(_('Endereço IP'), null=True, blank=True)
    user_agent = models.TextField(_('User Agent'), blank=True)
    details = models.JSONField(_('Detalhes'), default=dict, blank=True)
    
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Log de auditoria')
        verbose_name_plural = _('Logs de auditoria')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['event', '-created_at']),
        ]
    
    def __str__(self):
        user_str = self.user.username if self.user else 'Anonymous'
        return f"{user_str} - {self.event} - {self.created_at}"

