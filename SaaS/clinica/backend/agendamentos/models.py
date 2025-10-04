from django.db import models
from django.core.validators import RegexValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
import re


class Cliente(models.Model):
    nome = models.CharField(
        max_length=100,
        help_text="Nome completo do cliente"
    )
    whatsapp = models.CharField(
        max_length=20, 
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\+?[1-9]\d{10,14}$',
                message='WhatsApp deve ter formato válido (+5511999999999)'
            )
        ],
        help_text="WhatsApp no formato internacional"
    )
    email = models.EmailField(
        blank=True, 
        null=True,
        help_text="Email para confirmações (opcional)"
    )
    data_nascimento = models.DateField(
        blank=True, 
        null=True,
        help_text="Data de nascimento para controle de idade"
    )
    ativo = models.BooleanField(
        default=True,
        help_text="Cliente ativo no sistema"
    )
    observacoes = models.TextField(
        blank=True,
        help_text="Observações médicas/terapêuticas importantes"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nome']
        indexes = [
            models.Index(fields=['whatsapp']),
            models.Index(fields=['nome']),
            models.Index(fields=['ativo', 'criado_em']),
        ]

    def __str__(self):
        return self.nome

    def clean(self):
        """Validações customizadas"""
        if self.whatsapp:
            # Limpar formatação do WhatsApp
            self.whatsapp = re.sub(r'[^\d+]', '', self.whatsapp)
            if not self.whatsapp.startswith('+'):
                self.whatsapp = '+55' + self.whatsapp

    @property
    def idade(self):
        """Calcula idade baseada na data de nascimento"""
        if self.data_nascimento:
            today = timezone.now().date()
            return today.year - self.data_nascimento.year - (
                (today.month, today.day) < (self.data_nascimento.month, self.data_nascimento.day)
            )
        return None

    def total_agendamentos(self):
        """Retorna total de agendamentos do cliente"""
        return self.agendamento_set.count()

    def ultimo_agendamento(self):
        """Retorna último agendamento do cliente"""
        return self.agendamento_set.order_by('-horario').first()


class Servico(models.Model):
    nome = models.CharField(
        max_length=100,
        help_text="Nome do serviço oferecido"
    )
    descricao = models.TextField(
        blank=True,
        help_text="Descrição detalhada do serviço"
    )
    duracao_minutos = models.IntegerField(
        validators=[MinValueValidator(15)],
        help_text="Duração em minutos (mínimo 15)"
    )
    valor = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Valor do serviço em reais"
    )
    cor_calendario = models.CharField(
        max_length=7,
        default='#007bff',
        help_text="Cor para exibição no calendário (#RRGGBB)"
    )
    ativo = models.BooleanField(
        default=True,
        help_text="Serviço disponível para agendamento"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nome']
        indexes = [
            models.Index(fields=['ativo', 'nome']),
        ]

    def __str__(self):
        return f"{self.nome} - R$ {self.valor}"

    def agendamentos_mes_atual(self):
        """Agendamentos deste serviço no mês atual"""
        hoje = timezone.now()
        inicio_mes = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return self.agendamento_set.filter(
            horario__gte=inicio_mes,
            status__in=['confirmado', 'concluido']
        ).count()


class Agendamento(models.Model):
    STATUS_CHOICES = [
        ('confirmado', 'Confirmado'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado'),
        ('reagendado', 'Reagendado'),
        ('falta', 'Falta do Cliente'),
    ]

    cliente = models.ForeignKey(
        Cliente, 
        on_delete=models.CASCADE,
        help_text="Cliente do agendamento"
    )
    servico = models.ForeignKey(
        Servico, 
        on_delete=models.CASCADE,
        help_text="Serviço agendado"
    )
    horario = models.DateTimeField(
        help_text="Data e hora do agendamento"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,
        default='confirmado',
        help_text="Status atual do agendamento"
    )
    observacoes = models.TextField(
        blank=True,
        help_text="Observações específicas do agendamento"
    )
    valor_cobrado = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Valor efetivamente cobrado (pode diferir do valor padrão)"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-horario']
        indexes = [
            models.Index(fields=['horario']),
            models.Index(fields=['status', 'horario']),
            models.Index(fields=['cliente', 'horario']),
            models.Index(fields=['servico', 'horario']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['horario'],
                condition=models.Q(status='confirmado'),
                name='unique_confirmed_appointment_time'
            )
        ]

    def __str__(self):
        return f"{self.cliente.nome} - {self.servico.nome} ({self.horario})"

    def clean(self):
        """Validações customizadas"""
        if self.horario:
            # Não permitir agendamento no passado
            if self.horario < timezone.now():
                raise ValidationError("Não é possível agendar no passado")
            
            # Verificar conflito de horários apenas para agendamentos confirmados
            if self.status == 'confirmado':
                fim_agendamento = self.horario + timedelta(minutes=self.servico.duracao_minutos)
                
                conflitos = Agendamento.objects.filter(
                    status='confirmado',
                    horario__lt=fim_agendamento,
                    horario__gte=self.horario - timedelta(minutes=self.servico.duracao_minutos)
                ).exclude(pk=self.pk)
                
                if conflitos.exists():
                    raise ValidationError("Existe conflito de horário com outro agendamento")

    def save(self, *args, **kwargs):
        # Definir valor cobrado se não especificado
        if not self.valor_cobrado:
            self.valor_cobrado = self.servico.valor
        
        # Executar validações
        self.full_clean()
        
        super().save(*args, **kwargs)

    @property
    def horario_fim(self):
        """Calcula horário de fim baseado na duração do serviço"""
        return self.horario + timedelta(minutes=self.servico.duracao_minutos)

    @property
    def pode_cancelar(self):
        """Verifica se o agendamento pode ser cancelado"""
        return (
            self.status in ['confirmado'] and 
            self.horario > timezone.now() + timedelta(hours=2)
        )

    @property
    def esta_atrasado(self):
        """Verifica se o agendamento está atrasado"""
        return (
            self.status == 'confirmado' and 
            self.horario < timezone.now()
        )
