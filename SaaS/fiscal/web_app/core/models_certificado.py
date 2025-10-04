"""
Models para gestão de certificados digitais e consultas automáticas
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class CertificadoDigital(models.Model):
    """Armazena certificados digitais A1 para consultas automáticas"""

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificados')
    nome = models.CharField(max_length=200, help_text="Nome identificador do certificado")
    cnpj = models.CharField(max_length=14, db_index=True)

    # Certificado A1 (arquivo .pfx)
    arquivo_pfx = models.BinaryField(help_text="Arquivo .pfx do certificado")
    senha_pfx = models.CharField(max_length=255, help_text="Senha do certificado (criptografada)")

    # Metadados do certificado
    validade_inicio = models.DateField()
    validade_fim = models.DateField()
    emissor = models.CharField(max_length=255, blank=True)

    # Configurações de consulta
    ativo = models.BooleanField(default=True)
    consulta_automatica = models.BooleanField(default=False, help_text="Consultar automaticamente novos documentos")
    intervalo_consulta = models.IntegerField(default=60, help_text="Intervalo em minutos entre consultas")

    # Auditoria
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    ultima_consulta = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Certificado Digital"
        verbose_name_plural = "Certificados Digitais"
        ordering = ['-data_cadastro']

    def __str__(self):
        return f"{self.nome} - {self.cnpj}"

    def esta_valido(self):
        """Verifica se certificado está dentro da validade"""
        hoje = timezone.now().date()
        return self.validade_inicio <= hoje <= self.validade_fim


class ConsultaSEFAZ(models.Model):
    """Registro de consultas realizadas na SEFAZ"""

    TIPO_CHOICES = [
        ('NFE', 'Nota Fiscal Eletrônica'),
        ('CTE', 'Conhecimento de Transporte'),
        ('NFCE', 'NFC-e'),
        ('MDFE', 'Manifesto de Documentos Fiscais'),
    ]

    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('PROCESSANDO', 'Processando'),
        ('CONCLUIDA', 'Concluída'),
        ('ERRO', 'Erro'),
    ]

    certificado = models.ForeignKey(CertificadoDigital, on_delete=models.CASCADE, related_name='consultas')
    tipo_documento = models.CharField(max_length=10, choices=TIPO_CHOICES)

    # Período de consulta
    data_inicio = models.DateField()
    data_fim = models.DateField()

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDENTE')
    data_consulta = models.DateTimeField(auto_now_add=True)
    data_conclusao = models.DateTimeField(null=True, blank=True)

    # Resultados
    total_encontrados = models.IntegerField(default=0)
    total_importados = models.IntegerField(default=0)
    total_erros = models.IntegerField(default=0)

    # Log
    mensagem_erro = models.TextField(blank=True)
    log_detalhado = models.TextField(blank=True)

    class Meta:
        verbose_name = "Consulta SEFAZ"
        verbose_name_plural = "Consultas SEFAZ"
        ordering = ['-data_consulta']

    def __str__(self):
        return f"{self.tipo_documento} - {self.data_inicio} a {self.data_fim} - {self.status}"


class DocumentoConsultado(models.Model):
    """Documentos encontrados nas consultas"""

    PAPEL_CHOICES = [
        ('EMITENTE', 'Emitente'),
        ('DESTINATARIO', 'Destinatário'),
        ('TRANSPORTADOR', 'Transportador'),
        ('REMETENTE', 'Remetente'),
        ('EXPEDIDOR', 'Expedidor'),
        ('RECEBEDOR', 'Recebedor'),
        ('TOMADOR', 'Tomador'),
    ]

    consulta = models.ForeignKey(ConsultaSEFAZ, on_delete=models.CASCADE, related_name='documentos')

    # Identificação do documento
    chave_acesso = models.CharField(max_length=44, unique=True, db_index=True)
    numero = models.CharField(max_length=20)
    serie = models.CharField(max_length=10)
    data_emissao = models.DateTimeField()

    # Papel do CNPJ consultado neste documento
    papel_cnpj = models.CharField(max_length=20, choices=PAPEL_CHOICES)

    # Dados básicos
    emit_cnpj = models.CharField(max_length=14)
    emit_nome = models.CharField(max_length=255)
    dest_cnpj = models.CharField(max_length=14, blank=True)
    dest_nome = models.CharField(max_length=255, blank=True)
    valor_total = models.DecimalField(max_digits=15, decimal_places=2)

    # XML
    xml_completo = models.TextField(blank=True)
    xml_baixado = models.BooleanField(default=False)

    # Status
    importado = models.BooleanField(default=False)
    data_importacao = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Documento Consultado"
        verbose_name_plural = "Documentos Consultados"
        ordering = ['-data_emissao']
        indexes = [
            models.Index(fields=['chave_acesso']),
            models.Index(fields=['emit_cnpj']),
            models.Index(fields=['dest_cnpj']),
            models.Index(fields=['papel_cnpj']),
        ]

    def __str__(self):
        return f"{self.numero} - {self.emit_nome} - {self.papel_cnpj}"


class ConfiguracaoConsulta(models.Model):
    """Configurações globais de consulta"""

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='config_consulta')

    # UFs habilitadas para consulta
    ufs_habilitadas = models.CharField(
        max_length=500,
        default='SP,RJ,MG,RS,PR,SC,BA,PE,CE',
        help_text="UFs separadas por vírgula"
    )

    # Configurações de performance
    max_documentos_por_consulta = models.IntegerField(default=1000)
    timeout_consulta = models.IntegerField(default=300, help_text="Timeout em segundos")

    # Notificações
    notificar_email = models.BooleanField(default=True)
    email_notificacao = models.EmailField(blank=True)

    # Automação
    consulta_automatica_ativa = models.BooleanField(default=False)
    horario_consulta = models.TimeField(null=True, blank=True, help_text="Horário diário para consulta automática")

    class Meta:
        verbose_name = "Configuração de Consulta"
        verbose_name_plural = "Configurações de Consulta"

    def __str__(self):
        return f"Configuração de {self.usuario.username}"
