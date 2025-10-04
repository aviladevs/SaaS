"""
Models para gestão de XMLs fiscais (NFe e CTe)
"""
from django.db import models
from django.contrib.auth.models import User


class NFe(models.Model):
    """Nota Fiscal Eletrônica"""
    
    # Identificação
    chave_acesso = models.CharField(max_length=44, unique=True, db_index=True)
    numero_nf = models.CharField(max_length=20, null=True, blank=True)
    serie = models.CharField(max_length=10, null=True, blank=True)
    data_emissao = models.DateTimeField(null=True, blank=True, db_index=True)
    
    # Emitente
    emit_cnpj = models.CharField(max_length=14, null=True, blank=True, db_index=True)
    emit_nome = models.CharField(max_length=255, null=True, blank=True)
    emit_fantasia = models.CharField(max_length=255, null=True, blank=True)
    emit_ie = models.CharField(max_length=20, null=True, blank=True)
    emit_endereco = models.TextField(null=True, blank=True)
    emit_municipio = models.CharField(max_length=100, null=True, blank=True)
    emit_uf = models.CharField(max_length=2, null=True, blank=True)
    emit_cep = models.CharField(max_length=8, null=True, blank=True)
    
    # Destinatário
    dest_cnpj_cpf = models.CharField(max_length=14, null=True, blank=True, db_index=True)
    dest_nome = models.CharField(max_length=255, null=True, blank=True)
    dest_ie = models.CharField(max_length=20, null=True, blank=True)
    dest_endereco = models.TextField(null=True, blank=True)
    dest_municipio = models.CharField(max_length=100, null=True, blank=True)
    dest_uf = models.CharField(max_length=2, null=True, blank=True)
    dest_cep = models.CharField(max_length=8, null=True, blank=True)
    
    # Totais
    valor_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    valor_produtos = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    valor_icms = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    valor_ipi = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    valor_pis = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    valor_cofins = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    valor_tributos = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Status
    status_nfe = models.CharField(max_length=20, null=True, blank=True)
    protocolo = models.CharField(max_length=50, null=True, blank=True)
    motivo = models.TextField(null=True, blank=True)
    
    # XML e controle
    xml_content = models.TextField(null=True, blank=True)
    arquivo_nome = models.CharField(max_length=255, null=True, blank=True)
    data_importacao = models.DateTimeField(auto_now_add=True)
    usuario_importacao = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = "NFe - Nota Fiscal Eletrônica"
        verbose_name_plural = "NFe - Notas Fiscais Eletrônicas"
        ordering = ['-data_emissao']
        indexes = [
            models.Index(fields=['-data_emissao']),
            models.Index(fields=['emit_cnpj', '-data_emissao']),
        ]
    
    def __str__(self):
        return f"NFe {self.numero_nf} - {self.emit_nome}"


class NFeItem(models.Model):
    """Item de uma NFe"""
    
    nfe = models.ForeignKey(NFe, on_delete=models.CASCADE, related_name='itens')
    numero_item = models.IntegerField()
    
    # Produto
    codigo_produto = models.CharField(max_length=60, null=True, blank=True)
    descricao = models.TextField(null=True, blank=True)
    ncm = models.CharField(max_length=8, null=True, blank=True)
    cfop = models.CharField(max_length=4, null=True, blank=True)
    cest = models.CharField(max_length=7, null=True, blank=True)
    unidade = models.CharField(max_length=6, null=True, blank=True)
    quantidade = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    valor_unitario = models.DecimalField(max_digits=15, decimal_places=10, null=True, blank=True)
    valor_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    ean = models.CharField(max_length=14, null=True, blank=True)
    
    # Impostos
    valor_icms = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    valor_ipi = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    valor_pis = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    valor_cofins = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    class Meta:
        verbose_name = "Item de NFe"
        verbose_name_plural = "Itens de NFe"
        ordering = ['numero_item']
    
    def __str__(self):
        return f"Item {self.numero_item} - {self.descricao}"


class CTe(models.Model):
    """Conhecimento de Transporte Eletrônico"""
    
    # Identificação
    chave_acesso = models.CharField(max_length=44, unique=True, db_index=True)
    numero_ct = models.CharField(max_length=20, null=True, blank=True)
    serie = models.CharField(max_length=10, null=True, blank=True)
    data_emissao = models.DateTimeField(null=True, blank=True, db_index=True)
    
    # Emitente
    emit_cnpj = models.CharField(max_length=14, null=True, blank=True, db_index=True)
    emit_nome = models.CharField(max_length=255, null=True, blank=True)
    emit_fantasia = models.CharField(max_length=255, null=True, blank=True)
    emit_ie = models.CharField(max_length=20, null=True, blank=True)
    emit_endereco = models.TextField(null=True, blank=True)
    emit_municipio = models.CharField(max_length=100, null=True, blank=True)
    emit_uf = models.CharField(max_length=2, null=True, blank=True)
    
    # Remetente
    rem_cnpj = models.CharField(max_length=14, null=True, blank=True)
    rem_nome = models.CharField(max_length=255, null=True, blank=True)
    rem_ie = models.CharField(max_length=20, null=True, blank=True)
    rem_municipio = models.CharField(max_length=100, null=True, blank=True)
    rem_uf = models.CharField(max_length=2, null=True, blank=True)
    
    # Destinatário
    dest_cnpj = models.CharField(max_length=14, null=True, blank=True)
    dest_nome = models.CharField(max_length=255, null=True, blank=True)
    dest_ie = models.CharField(max_length=20, null=True, blank=True)
    dest_municipio = models.CharField(max_length=100, null=True, blank=True)
    dest_uf = models.CharField(max_length=2, null=True, blank=True)
    
    # Transporte
    modal = models.CharField(max_length=2, null=True, blank=True)
    tipo_servico = models.CharField(max_length=1, null=True, blank=True)
    cfop = models.CharField(max_length=4, null=True, blank=True)
    natureza_operacao = models.CharField(max_length=255, null=True, blank=True)
    municipio_inicio = models.CharField(max_length=100, null=True, blank=True)
    uf_inicio = models.CharField(max_length=2, null=True, blank=True)
    municipio_fim = models.CharField(max_length=100, null=True, blank=True)
    uf_fim = models.CharField(max_length=2, null=True, blank=True)
    
    # Valores
    valor_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    valor_receber = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    valor_carga = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    valor_icms = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Status
    status_cte = models.CharField(max_length=20, null=True, blank=True)
    protocolo = models.CharField(max_length=50, null=True, blank=True)
    motivo = models.TextField(null=True, blank=True)
    
    # XML e controle
    xml_content = models.TextField(null=True, blank=True)
    arquivo_nome = models.CharField(max_length=255, null=True, blank=True)
    data_importacao = models.DateTimeField(auto_now_add=True)
    usuario_importacao = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = "CTe - Conhecimento de Transporte"
        verbose_name_plural = "CTe - Conhecimentos de Transporte"
        ordering = ['-data_emissao']
        indexes = [
            models.Index(fields=['-data_emissao']),
            models.Index(fields=['emit_cnpj', '-data_emissao']),
        ]
    
    def __str__(self):
        return f"CTe {self.numero_ct} - {self.emit_nome}"


class ImportLog(models.Model):
    """Log de importações"""
    
    TIPO_CHOICES = [
        ('NFe', 'NFe - Nota Fiscal'),
        ('CTe', 'CTe - Conhecimento Transporte'),
    ]
    
    STATUS_CHOICES = [
        ('sucesso', 'Sucesso'),
        ('erro', 'Erro'),
        ('processando', 'Processando'),
    ]
    
    data_importacao = models.DateTimeField(auto_now_add=True)
    tipo_documento = models.CharField(max_length=10, choices=TIPO_CHOICES)
    arquivo_nome = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processando')
    mensagem = models.TextField(null=True, blank=True)
    chave_acesso = models.CharField(max_length=44, null=True, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = "Log de Importação"
        verbose_name_plural = "Logs de Importação"
        ordering = ['-data_importacao']
    
    def __str__(self):
        return f"{self.tipo_documento} - {self.arquivo_nome} ({self.status})"
