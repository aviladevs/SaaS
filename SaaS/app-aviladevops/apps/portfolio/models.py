from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, URLValidator
from django.utils.text import slugify


class ProjectCategory(models.Model):
    """Categorias de projetos"""

    name = models.CharField(_('Nome'), max_length=100)
    slug = models.SlugField(_('Slug'), unique=True, blank=True)
    description = models.TextField(_('Descrição'), blank=True)
    color = models.CharField(_('Cor'), max_length=7, default='#007bf')
    is_active = models.BooleanField(_('Ativo'), default=True)
    order = models.PositiveIntegerField(_('Ordem'), default=0)

    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)

    class Meta:
        verbose_name = _('Categoria de Projeto')
        verbose_name_plural = _('Categorias de Projetos')
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Project(models.Model):
    """Modelo de projeto do portfólio"""

    # Informações básicas
    title = models.CharField(_('Título'), max_length=200)
    slug = models.SlugField(_('Slug'), unique=True, blank=True)
    description = models.TextField(_('Descrição'))
    short_description = models.CharField(_('Descrição curta'), max_length=300, blank=True)

    # Categoria e cliente
    category = models.ForeignKey(
        ProjectCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='projects',
        verbose_name=_('Categoria')
    )
    client = models.CharField(_('Cliente'), max_length=100, blank=True)
    client_website = models.URLField(_('Website do cliente'), blank=True, validators=[URLValidator()])

    # URLs e repositórios
    project_url = models.URLField(_('URL do projeto'), blank=True, validators=[URLValidator()])
    github_url = models.URLField(_('URL do GitHub'), blank=True, validators=[URLValidator()])
    demo_url = models.URLField(_('URL da demo'), blank=True, validators=[URLValidator()])

    # Tecnologias e recursos
    technologies = models.JSONField(_('Tecnologias'), default=list)
    features = models.JSONField(_('Características'), default=list)

    # Mídia
    featured_image = models.ImageField(_('Imagem destacada'), upload_to='portfolio/featured/')
    gallery = models.JSONField(_('Galeria'), default=list)

    # Métricas e resultados
    start_date = models.DateField(_('Data de início'), null=True, blank=True)
    end_date = models.DateField(_('Data de fim'), null=True, blank=True)
    budget = models.DecimalField(
        _('Orçamento'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )

    results = models.TextField(_('Resultados obtidos'), blank=True)
    challenges = models.TextField(_('Desafios enfrentados'), blank=True)
    learnings = models.TextField(_('Aprendizados'), blank=True)

    # Configurações
    is_featured = models.BooleanField(_('Projeto destacado'), default=False)
    is_completed = models.BooleanField(_('Projeto concluído'), default=True)
    is_public = models.BooleanField(_('Projeto público'), default=True)
    show_in_homepage = models.BooleanField(_('Mostrar na homepage'), default=False)

    # SEO
    meta_title = models.CharField(_('Meta título'), max_length=60, blank=True)
    meta_description = models.CharField(_('Meta descrição'), max_length=160, blank=True)

    # Controle
    order = models.PositiveIntegerField(_('Ordem'), default=0)
    views_count = models.PositiveIntegerField(_('Visualizações'), default=0)

    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)

    class Meta:
        verbose_name = _('Projeto')
        verbose_name_plural = _('Projetos')
        ordering = ['-is_featured', 'order', '-created_at']

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

    @property
    def duration(self):
        """Calcula duração do projeto em meses"""
        if self.start_date and self.end_date:
            return (self.end_date.year - self.start_date.year) * 12 + (self.end_date.month - self.start_date.month)
        return None


class ProjectImage(models.Model):
    """Imagens do projeto"""

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('Projeto')
    )

    image = models.ImageField(_('Imagem'), upload_to='portfolio/images/')
    caption = models.CharField(_('Legenda'), max_length=200, blank=True)
    order = models.PositiveIntegerField(_('Ordem'), default=0)
    is_featured = models.BooleanField(_('Imagem destacada'), default=False)

    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)

    class Meta:
        verbose_name = _('Imagem do Projeto')
        verbose_name_plural = _('Imagens do Projeto')
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.project.title} - {self.caption or 'Imagem'}"


class Testimonial(models.Model):
    """Depoimentos de clientes"""

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='testimonials',
        verbose_name=_('Projeto')
    )

    client_name = models.CharField(_('Nome do cliente'), max_length=100)
    client_position = models.CharField(_('Cargo'), max_length=100, blank=True)
    client_company = models.CharField(_('Empresa'), max_length=100, blank=True)
    client_avatar = models.ImageField(_('Foto do cliente'), upload_to='testimonials/', blank=True, null=True)

    testimonial = models.TextField(_('Depoimento'))
    rating = models.PositiveIntegerField(_('Avaliação'), default=5, help_text='De 1 a 5 estrelas')

    is_featured = models.BooleanField(_('Depoimento destacado'), default=False)
    is_active = models.BooleanField(_('Ativo'), default=True)

    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)

    class Meta:
        verbose_name = _('Depoimento')
        verbose_name_plural = _('Depoimentos')
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return f"Depoimento de {self.client_name}"
