# Ávila DevOps SaaS - Módulo Ferro Velho
# Integração da aplicação específica de controle de sucata

from django.apps import AppConfig
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify


class FerroVelhoConfig(AppConfig):
    """Configuração da aplicação Ferro Velho"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ferrovelho'
    verbose_name = 'Ferro Velho'

    def ready(self):
        import apps.ferrovelho.signals


class SucataEntry(models.Model):
    """Entrada de sucata no ferro velho"""

    # Relacionamento com tenant
    tenant = models.ForeignKey(
        'users.Tenant',
        on_delete=models.CASCADE,
        related_name='sucata_entries',
        verbose_name=_('Tenant')
    )

    # Informações básicas
    cliente = models.CharField(_('Cliente'), max_length=200)
    data = models.DateField(_('Data'), auto_now_add=True)
    hora = models.TimeField(_('Hora'), auto_now_add=True)
    observacoes = models.TextField(_('Observações'), blank=True)

    # Status
    is_processed = models.BooleanField(_('Processado'), default=False)
    processed_at = models.DateTimeField(_('Processado em'), null=True, blank=True)

    # Controle
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_sucata_entries',
        verbose_name=_('Criado por')
    )

    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)

    class Meta:
        verbose_name = _('Entrada de Sucata')
        verbose_name_plural = _('Entradas de Sucata')
        ordering = ['-data', '-hora']
        unique_together = ['tenant', 'cliente', 'data', 'hora']

    def __str__(self):
        return f"{self.cliente} - {self.data} {self.hora}"

    def save(self, *args, **kwargs):
        # Se está sendo marcado como processado
        if self.is_processed and not self.processed_at:
            from django.utils import timezone
            self.processed_at = timezone.now()
        super().save(*args, **kwargs)


class SucataMaterial(models.Model):
    """Materiais de sucata com seus preços"""

    # Relacionamento com tenant
    tenant = models.ForeignKey(
        'users.Tenant',
        on_delete=models.CASCADE,
        related_name='sucata_materials',
        verbose_name=_('Tenant')
    )

    # Informações do material
    nome = models.CharField(_('Nome do Material'), max_length=100, unique=True)
    categoria = models.CharField(_('Categoria'), max_length=50)
    unidade = models.CharField(_('Unidade'), max_length=10, default='kg')

    # Preços
    preco_base = models.DecimalField(_('Preço Base'), max_digits=10, decimal_places=2)
    preco_atual = models.DecimalField(_('Preço Atual'), max_digits=10, decimal_places=2)

    # Controle
    is_active = models.BooleanField(_('Ativo'), default=True)
    order = models.PositiveIntegerField(_('Ordem'), default=0)

    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)

    class Meta:
        verbose_name = _('Material de Sucata')
        verbose_name_plural = _('Materiais de Sucata')
        ordering = ['categoria', 'order', 'nome']

    def __str__(self):
        return f"{self.nome} ({self.categoria})"


class SucataItem(models.Model):
    """Itens de uma entrada de sucata"""

    # Relacionamento com entrada
    entrada = models.ForeignKey(
        SucataEntry,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Entrada')
    )

    # Relacionamento com material
    material = models.ForeignKey(
        SucataMaterial,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Material')
    )

    # Quantidade
    quantidade = models.DecimalField(_('Quantidade'), max_digits=10, decimal_places=2)
    valor_unitario = models.DecimalField(_('Valor Unitário'), max_digits=10, decimal_places=2)
    valor_total = models.DecimalField(_('Valor Total'), max_digits=10, decimal_places=2)

    # Controle
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)

    class Meta:
        verbose_name = _('Item de Sucata')
        verbose_name_plural = _('Itens de Sucata')
        ordering = ['material__categoria', 'material__nome']

    def save(self, *args, **kwargs):
        # Calcular valor total automaticamente
        if self.quantidade and self.valor_unitario:
            self.valor_total = self.quantidade * self.valor_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.material.nome}: {self.quantidade} {self.material.unidade}"


class RelatorioSucata(models.Model):
    """Relatórios de sucata gerados"""

    # Relacionamento com tenant
    tenant = models.ForeignKey(
        'users.Tenant',
        on_delete=models.CASCADE,
        related_name='sucata_reports',
        verbose_name=_('Tenant')
    )

    # Informações do relatório
    titulo = models.CharField(_('Título'), max_length=200)
    descricao = models.TextField(_('Descrição'), blank=True)

    # Período do relatório
    data_inicio = models.DateField(_('Data Início'))
    data_fim = models.DateField(_('Data Fim'))

    # Filtros aplicados
    filtros = models.JSONField(_('Filtros'), default=dict)

    # Arquivo gerado
    arquivo_pdf = models.FileField(_('Arquivo PDF'), upload_to='relatorios/sucata/')
    arquivo_excel = models.FileField(_('Arquivo Excel'), upload_to='relatorios/sucata/')

    # Controle
    gerado_por = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='gerados_sucata_reports',
        verbose_name=_('Gerado por')
    )

    gerado_em = models.DateTimeField(_('Gerado em'), auto_now_add=True)

    class Meta:
        verbose_name = _('Relatório de Sucata')
        verbose_name_plural = _('Relatórios de Sucata')
        ordering = ['-gerado_em']

    def __str__(self):
        return f"{self.titulo} ({self.data_inicio} a {self.data_fim})"


# Função para popular materiais iniciais
def populate_initial_materials(tenant):
    """Popular materiais iniciais para um tenant"""

    materiais_iniciais = [
        # Chaparia e metais básicos
        {'nome': 'Chaparia', 'categoria': 'Ferro', 'preco_base': 0.80, 'preco_atual': 0.80},
        {'nome': 'Miúda', 'categoria': 'Ferro', 'preco_base': 0.75, 'preco_atual': 0.75},
        {'nome': 'Estamparia', 'categoria': 'Ferro', 'preco_base': 0.85, 'preco_atual': 0.85},
        {'nome': 'Fundido', 'categoria': 'Ferro', 'preco_base': 0.90, 'preco_atual': 0.90},
        {'nome': 'Cavaco', 'categoria': 'Ferro', 'preco_base': 0.70, 'preco_atual': 0.70},

        # Mola
        {'nome': 'Mola escolha', 'categoria': 'Mola', 'preco_base': 1.20, 'preco_atual': 1.20},

        # Filtros
        {'nome': 'Filtro óleo', 'categoria': 'Filtros', 'preco_base': 0.50, 'preco_atual': 0.50},

        # Alumínio
        {'nome': 'Alumínio - Latinha', 'categoria': 'Alumínio', 'preco_base': 4.50, 'preco_atual': 4.50},
        {'nome': 'Alumínio - Chaparia', 'categoria': 'Alumínio', 'preco_base': 3.80, 'preco_atual': 3.80},
        {'nome': 'Alumínio - Bloco', 'categoria': 'Alumínio', 'preco_base': 4.20, 'preco_atual': 4.20},
        {'nome': 'Alumínio - Panela', 'categoria': 'Alumínio', 'preco_base': 3.50, 'preco_atual': 3.50},
        {'nome': 'Alumínio - Perfil Novo', 'categoria': 'Alumínio', 'preco_base': 5.00, 'preco_atual': 5.00},
        {'nome': 'Alumínio - Perfil Pintado', 'categoria': 'Alumínio', 'preco_base': 4.80, 'preco_atual': 4.80},
        {'nome': 'Alumínio - Radiador', 'categoria': 'Alumínio', 'preco_base': 4.00, 'preco_atual': 4.00},
        {'nome': 'Alumínio - Roda', 'categoria': 'Alumínio', 'preco_base': 6.00, 'preco_atual': 6.00},
        {'nome': 'Alumínio - Cavaco', 'categoria': 'Alumínio', 'preco_base': 3.00, 'preco_atual': 3.00},
        {'nome': 'Alumínio - Estamparia', 'categoria': 'Alumínio', 'preco_base': 3.50, 'preco_atual': 3.50},
        {'nome': 'Alumínio - Off-set', 'categoria': 'Alumínio', 'preco_base': 4.50, 'preco_atual': 4.50},

        # Baterias e metais especiais
        {'nome': 'Bateria', 'categoria': 'Baterias', 'preco_base': 2.50, 'preco_atual': 2.50},
        {'nome': 'Chumbo', 'categoria': 'Metais', 'preco_base': 3.20, 'preco_atual': 3.20},

        # Cobre
        {'nome': 'Cobre - Mel', 'categoria': 'Cobre', 'preco_base': 25.00, 'preco_atual': 25.00},
        {'nome': 'Cobre - Misto', 'categoria': 'Cobre', 'preco_base': 22.00, 'preco_atual': 22.00},
        {'nome': 'Radiador Alum. Cobre', 'categoria': 'Cobre', 'preco_base': 18.00, 'preco_atual': 18.00},
        {'nome': 'Cobre Encapado', 'categoria': 'Cobre', 'preco_base': 20.00, 'preco_atual': 20.00},

        # Latão e metais diversos
        {'nome': 'Metal Latão', 'categoria': 'Metais', 'preco_base': 12.00, 'preco_atual': 12.00},
        {'nome': 'Cavaco Metal', 'categoria': 'Metais', 'preco_base': 8.00, 'preco_atual': 8.00},
        {'nome': 'Radiador Metal', 'categoria': 'Metais', 'preco_base': 15.00, 'preco_atual': 15.00},

        # Bronze
        {'nome': 'Bronze', 'categoria': 'Bronze', 'preco_base': 14.00, 'preco_atual': 14.00},
        {'nome': 'Cavaco Bronze', 'categoria': 'Bronze', 'preco_base': 10.00, 'preco_atual': 10.00},

        # Inox
        {'nome': 'Inox 304', 'categoria': 'Inox', 'preco_base': 8.00, 'preco_atual': 8.00},
        {'nome': 'Inox 430', 'categoria': 'Inox', 'preco_base': 6.50, 'preco_atual': 6.50},

        # Materiais especiais
        {'nome': 'Material Sujo', 'categoria': 'Outros', 'preco_base': 0.30, 'preco_atual': 0.30},
        {'nome': 'Magnésio', 'categoria': 'Outros', 'preco_base': 5.00, 'preco_atual': 5.00},
        {'nome': 'Antimônio', 'categoria': 'Outros', 'preco_base': 8.00, 'preco_atual': 8.00},
    ]

    for mat in materiais_iniciais:
        SucataMaterial.objects.get_or_create(
            tenant=tenant,
            nome=mat['nome'],
            defaults={
                'categoria': mat['categoria'],
                'preco_base': mat['preco_base'],
                'preco_atual': mat['preco_atual'],
                'unidade': 'kg'
            }
        )
