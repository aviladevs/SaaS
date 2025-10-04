from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class ContactMessage(models.Model):
    """Mensagens de contato"""

    PRIORITY_CHOICES = [
        ('low', _('Baixa')),
        ('medium', _('Média')),
        ('high', _('Alta')),
        ('urgent', _('Urgente')),
    ]

    STATUS_CHOICES = [
        ('new', _('Novo')),
        ('in_progress', _('Em Andamento')),
        ('waiting_response', _('Aguardando Resposta')),
        ('resolved', _('Resolvido')),
        ('closed', _('Fechado')),
    ]

    SOURCE_CHOICES = [
        ('website', _('Website')),
        ('whatsapp', _('WhatsApp')),
        ('email', _('Email')),
        ('phone', _('Telefone')),
        ('social_media', _('Redes Sociais')),
        ('referral', _('Indicação')),
    ]

    # Informações do contato
    name = models.CharField(_('Nome'), max_length=100)
    email = models.EmailField(_('Email'))
    phone = models.CharField(_('Telefone'), max_length=20, blank=True)
    company = models.CharField(_('Empresa'), max_length=100, blank=True)
    position = models.CharField(_('Cargo'), max_length=50, blank=True)

    # Mensagem
    subject = models.CharField(_('Assunto'), max_length=200)
    message = models.TextField(_('Mensagem'))

    # Metadados
    source = models.CharField(_('Fonte'), max_length=20, choices=SOURCE_CHOICES, default='website')
    priority = models.CharField(_('Prioridade'), max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='new')

    # Relacionamentos
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_contacts',
        verbose_name=_('Responsável')
    )

    # Controle
    ip_address = models.GenericIPAddressField(_('IP do remetente'), blank=True, null=True)
    user_agent = models.TextField(_('User Agent'), blank=True)

    is_read = models.BooleanField(_('Lido'), default=False)
    is_archived = models.BooleanField(_('Arquivado'), default=False)

    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)
    resolved_at = models.DateTimeField(_('Resolvido em'), null=True, blank=True)

    class Meta:
        verbose_name = _('Mensagem de Contato')
        verbose_name_plural = _('Mensagens de Contato')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"

    def mark_as_read(self):
        """Marca mensagem como lida"""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])

    def resolve(self):
        """Marca mensagem como resolvida"""
        self.status = 'resolved'
        self.resolved_at = models.functions.Now()
        self.save()


class ContactNote(models.Model):
    """Notas internas sobre contatos"""

    contact = models.ForeignKey(
        ContactMessage,
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name=_('Contato')
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='contact_notes',
        verbose_name=_('Autor')
    )

    content = models.TextField(_('Conteúdo'))
    is_internal = models.BooleanField(_('Nota interna'), default=True)

    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)

    class Meta:
        verbose_name = _('Nota de Contato')
        verbose_name_plural = _('Notas de Contato')
        ordering = ['created_at']

    def __str__(self):
        return f"Nota de {self.author.username} em {self.contact.name}"


class FAQ(models.Model):
    """Perguntas frequentes"""

    question = models.CharField(_('Pergunta'), max_length=300)
    answer = models.TextField(_('Resposta'))

    category = models.CharField(_('Categoria'), max_length=100, blank=True)
    order = models.PositiveIntegerField(_('Ordem'), default=0)
    is_active = models.BooleanField(_('Ativo'), default=True)

    views_count = models.PositiveIntegerField(_('Visualizações'), default=0)
    helpful_count = models.PositiveIntegerField(_('Útil'), default=0)

    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)

    class Meta:
        verbose_name = _('FAQ')
        verbose_name_plural = _('FAQs')
        ordering = ['order', 'question']

    def __str__(self):
        return self.question

    def increment_views(self):
        """Incrementa contador de visualizações"""
        self.views_count += 1
        self.save(update_fields=['views_count'])


class ContactSetting(models.Model):
    """Configurações de contato"""

    auto_reply_enabled = models.BooleanField(_('Resposta automática ativada'), default=True)
    auto_reply_message = models.TextField(_('Mensagem de resposta automática'), blank=True)

    notification_emails = models.JSONField(_('Emails de notificação'), default=list)
    whatsapp_notifications = models.BooleanField(_('Notificações WhatsApp'), default=True)

    business_hours_start = models.TimeField(_('Início do expediente'), default='08:00')
    business_hours_end = models.TimeField(_('Fim do expediente'), default='18:00')
    business_days = models.JSONField(_('Dias úteis'), default=[1, 2, 3, 4, 5])  # Segunda a Sexta

    response_time_hours = models.PositiveIntegerField(_('Tempo de resposta (horas)'), default=24)

    class Meta:
        verbose_name = _('Configuração de Contato')
        verbose_name_plural = _('Configurações de Contato')

    def __str__(self):
        return 'Configurações de Contato'
