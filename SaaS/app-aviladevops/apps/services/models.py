from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils.text import slugify


class ServiceCategory(models.Model):
    """Categoria de serviços"""

    name = models.CharField(_('Nome'), max_length=100)
    slug = models.SlugField(_('Slug'), unique=True, blank=True)
    description = models.TextField(_('Descrição'), blank=True)
    icon = models.CharField(_('Ícone'), max_length=50, help_text='Nome do ícone do Font Awesome')
    color = models.CharField(_('Cor'), max_length=7, default='#007bf', help_text='Cor em hexadecimal')
    is_active = models.BooleanField(_('Ativo'), default=True)
    order = models.PositiveIntegerField(_('Ordem'), default=0)

    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)

    class Meta:
        verbose_name = _('Categoria de Serviço')
        verbose_name_plural = _('Categorias de Serviços')
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Service(models.Model):
    """Modelo de serviço oferecido"""

    # Informações básicas
    title = models.CharField(_('Título'), max_length=200)
    slug = models.SlugField(_('Slug'), unique=True, blank=True)
    description = models.TextField(_('Descrição'))
    short_description = models.CharField(_('Descrição curta'), max_length=300, blank=True)

    # Categoria e organização
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.CASCADE,
        related_name='services',
        verbose_name=_('Categoria')
    )

    # Preços
    price = models.DecimalField(
        _('Preço'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text=_('Preço base do serviço')
    )
    price_type = models.CharField(
        _('Tipo de preço'),
        max_length=20,
        choices=[
            ('fixed', _('Preço Fixo')),
            ('hourly', _('Por Hora')),
            ('project', _('Por Projeto')),
            ('monthly', _('Mensal')),
        ],
        default='project'
    )

    # Recursos e funcionalidades
    features = models.JSONField(_('Recursos'), default=list, help_text=_('Lista de recursos incluídos'))
    technologies = models.JSONField(_('Tecnologias'), default=list, help_text=_('Tecnologias utilizadas'))

    # Mídia
    image = models.ImageField(_('Imagem'), upload_to='services/', blank=True, null=True)
    gallery = models.JSONField(_('Galeria'), default=list, help_text=_('URLs de imagens da galeria'))

    # Configurações
    is_featured = models.BooleanField(_('Destaque'), default=False)
    is_active = models.BooleanField(_('Ativo'), default=True)
    is_popular = models.BooleanField(_('Popular'), default=False)

    # SEO
    meta_title = models.CharField(_('Meta título'), max_length=60, blank=True)
    meta_description = models.CharField(_('Meta descrição'), max_length=160, blank=True)

    # Controle
    order = models.PositiveIntegerField(_('Ordem'), default=0)
    views_count = models.PositiveIntegerField(_('Visualizações'), default=0)

    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)

    class Meta:
        verbose_name = _('Serviço')
        verbose_name_plural = _('Serviços')
        ordering = ['order', '-is_featured', 'title']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.short_description and self.description:
            self.short_description = self.description[:300] + '...' if len(self.description) > 300 else self.description
        if not self.meta_title:
            self.meta_title = self.title[:60]
        if not self.meta_description and self.description:
            self.meta_description = self.description[:160]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def increment_views(self):
        """Incrementa contador de visualizações"""
        self.views_count += 1
        self.save(update_fields=['views_count'])


class ServicePackage(models.Model):
    """Pacotes de serviços"""

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='packages',
        verbose_name=_('Serviço')
    )

    name = models.CharField(_('Nome'), max_length=100)
    description = models.TextField(_('Descrição'))
    price = models.DecimalField(
        _('Preço'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    features = models.JSONField(_('Recursos incluídos'), default=list)
    is_popular = models.BooleanField(_('Popular'), default=False)
    is_active = models.BooleanField(_('Ativo'), default=True)

    order = models.PositiveIntegerField(_('Ordem'), default=0)

    class Meta:
        verbose_name = _('Pacote de Serviço')
        verbose_name_plural = _('Pacotes de Serviços')
        ordering = ['order']

    def __str__(self):
        return f"{self.service.title} - {self.name}"
