from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse


class BlogCategory(models.Model):
    """Categorias do blog"""

    name = models.CharField(_('Nome'), max_length=100)
    slug = models.SlugField(_('Slug'), unique=True, blank=True)
    description = models.TextField(_('Descrição'), blank=True)
    color = models.CharField(_('Cor'), max_length=7, default='#007bff')
    is_active = models.BooleanField(_('Ativo'), default=True)
    order = models.PositiveIntegerField(_('Ordem'), default=0)

    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)

    class Meta:
        verbose_name = _('Categoria do Blog')
        verbose_name_plural = _('Categorias do Blog')
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Tags para artigos"""

    name = models.CharField(_('Nome'), max_length=50, unique=True)
    slug = models.SlugField(_('Slug'), unique=True, blank=True)
    color = models.CharField(_('Cor'), max_length=7, default='#6c757d')
    is_active = models.BooleanField(_('Ativo'), default=True)

    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)

    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Article(models.Model):
    """Modelo de artigo do blog"""

    STATUS_CHOICES = [
        ('draft', _('Rascunho')),
        ('published', _('Publicado')),
        ('archived', _('Arquivado')),
    ]

    # Informações básicas
    title = models.CharField(_('Título'), max_length=200)
    slug = models.SlugField(_('Slug'), unique=True, blank=True)
    excerpt = models.CharField(_('Resumo'), max_length=500, blank=True)
    content = models.TextField(_('Conteúdo'))

    # Autor e categoria
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='articles',
        verbose_name=_('Autor')
    )
    category = models.ForeignKey(
        BlogCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articles',
        verbose_name=_('Categoria')
    )

    # Tags e tópicos relacionados
    tags = models.ManyToManyField(
        Tag,
        related_name='articles',
        verbose_name=_('Tags'),
        blank=True
    )

    # Mídia
    featured_image = models.ImageField(_('Imagem destacada'), upload_to='blog/featured/')
    gallery = models.JSONField(_('Galeria'), default=list)

    # SEO e metadados
    meta_title = models.CharField(_('Meta título'), max_length=60, blank=True)
    meta_description = models.CharField(_('Meta descrição'), max_length=160, blank=True)

    # Configurações
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(_('Artigo destacado'), default=False)
    allow_comments = models.BooleanField(_('Permitir comentários'), default=True)

    # Controle de publicação
    published_at = models.DateTimeField(_('Publicado em'), null=True, blank=True)
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)

    # Métricas
    views_count = models.PositiveIntegerField(_('Visualizações'), default=0)
    likes_count = models.PositiveIntegerField(_('Curtidas'), default=0)
    comments_count = models.PositiveIntegerField(_('Comentários'), default=0)

    class Meta:
        verbose_name = _('Artigo')
        verbose_name_plural = _('Artigos')
        ordering = ['-published_at', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        # Auto-generate excerpt if not provided
        if not self.excerpt and self.content:
            # Remove HTML tags and get first 500 characters
            import re
            clean_content = re.sub(r'<[^>]+>', '', self.content)
            self.excerpt = clean_content[:500] + '...' if len(clean_content) > 500 else clean_content

        # Auto-generate meta fields if not provided
        if not self.meta_title:
            self.meta_title = self.title[:60]
        if not self.meta_description and self.excerpt:
            self.meta_description = self.excerpt[:160]

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """URL absoluta do artigo"""
        if self.published_at:
            return reverse('blog:article_detail', kwargs={'slug': self.slug})
        return '#'

    def increment_views(self):
        """Incrementa contador de visualizações"""
        self.views_count += 1
        self.save(update_fields=['views_count'])

    def is_published(self):
        """Verifica se artigo está publicado"""
        return self.status == 'published' and self.published_at is not None


class Comment(models.Model):
    """Comentários de artigos"""

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('Artigo')
    )

    author_name = models.CharField(_('Nome do autor'), max_length=100)
    author_email = models.EmailField(_('Email do autor'))
    author_website = models.URLField(_('Website'), blank=True)

    content = models.TextField(_('Comentário'))
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name=_('Comentário pai')
    )

    is_approved = models.BooleanField(_('Aprovado'), default=False)
    is_spam = models.BooleanField(_('Spam'), default=False)

    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)

    class Meta:
        verbose_name = _('Comentário')
        verbose_name_plural = _('Comentários')
        ordering = ['created_at']

    def __str__(self):
        return f"Comentário de {self.author_name} em {self.article.title}"


class Newsletter(models.Model):
    """Inscrições na newsletter"""

    email = models.EmailField(_('Email'), unique=True)
    name = models.CharField(_('Nome'), max_length=100, blank=True)
    is_active = models.BooleanField(_('Ativo'), default=True)

    subscribed_at = models.DateTimeField(_('Inscrito em'), auto_now_add=True)
    unsubscribed_at = models.DateTimeField(_('Cancelado em'), null=True, blank=True)

    source = models.CharField(_('Fonte'), max_length=50, default='website')

    class Meta:
        verbose_name = _('Newsletter')
        verbose_name_plural = _('Newsletters')
        ordering = ['-subscribed_at']

    def __str__(self):
        return self.email
