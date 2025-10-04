from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import Cliente, Servico, Agendamento


class ClienteSerializer(serializers.ModelSerializer):
    """Serializer completo para Cliente com validações"""
    
    idade = serializers.ReadOnlyField()
    total_agendamentos = serializers.ReadOnlyField()
    ultimo_agendamento = serializers.SerializerMethodField()
    
    class Meta:
        model = Cliente
        fields = [
            'id', 'nome', 'whatsapp', 'email', 'data_nascimento',
            'ativo', 'observacoes', 'criado_em', 'atualizado_em',
            'idade', 'total_agendamentos', 'ultimo_agendamento'
        ]
        read_only_fields = ['criado_em', 'atualizado_em']

    def get_ultimo_agendamento(self, obj):
        """Retorna dados do último agendamento"""
        ultimo = obj.ultimo_agendamento()
        if ultimo:
            return {
                'id': ultimo.id,
                'horario': ultimo.horario,
                'servico': ultimo.servico.nome,
                'status': ultimo.status
            }
        return None

    def validate_whatsapp(self, value):
        """Validação específica para WhatsApp"""
        import re
        # Remover caracteres não numéricos exceto +
        clean_number = re.sub(r'[^\d+]', '', value)
        
        if not clean_number.startswith('+'):
            clean_number = '+55' + clean_number
            
        if len(clean_number) < 13 or len(clean_number) > 16:
            raise serializers.ValidationError(
                "WhatsApp deve ter entre 13 e 16 dígitos incluindo código do país"
            )
        
        return clean_number

    def validate_email(self, value):
        """Validação específica para email"""
        if value and Cliente.objects.filter(email=value).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError("Este email já está em uso")
        return value


class ServicoSerializer(serializers.ModelSerializer):
    """Serializer completo para Serviço com métricas"""
    
    agendamentos_mes_atual = serializers.ReadOnlyField()
    
    class Meta:
        model = Servico
        fields = [
            'id', 'nome', 'descricao', 'duracao_minutos', 'valor',
            'cor_calendario', 'ativo', 'criado_em', 'atualizado_em',
            'agendamentos_mes_atual'
        ]
        read_only_fields = ['criado_em', 'atualizado_em']

    def validate_duracao_minutos(self, value):
        """Validação para duração do serviço"""
        if value < 15:
            raise serializers.ValidationError("Duração mínima é de 15 minutos")
        if value > 480:  # 8 horas
            raise serializers.ValidationError("Duração máxima é de 8 horas")
        if value % 15 != 0:
            raise serializers.ValidationError("Duração deve ser múltipla de 15 minutos")
        return value

    def validate_valor(self, value):
        """Validação para valor do serviço"""
        if value <= 0:
            raise serializers.ValidationError("Valor deve ser maior que zero")
        if value > 10000:
            raise serializers.ValidationError("Valor máximo é R$ 10.000,00")
        return value


class AgendamentoCreateSerializer(serializers.ModelSerializer):
    """Serializer específico para criação de agendamentos"""
    
    class Meta:
        model = Agendamento
        fields = [
            'cliente', 'servico', 'horario', 'observacoes', 'valor_cobrado'
        ]

    def validate_horario(self, value):
        """Validação específica para horário"""
        now = timezone.now()
        
        # Não permitir agendamento no passado
        if value < now:
            raise serializers.ValidationError("Não é possível agendar no passado")
        
        # Não permitir agendamento muito distante (1 ano)
        if value > now + timedelta(days=365):
            raise serializers.ValidationError("Não é possível agendar com mais de 1 ano de antecedência")
        
        # Verificar horário comercial (8h às 19h)
        if value.hour < 8 or value.hour >= 19:
            raise serializers.ValidationError("Agendamentos devem ser entre 8h e 19h")
        
        # Verificar se não é domingo
        if value.weekday() == 6:  # 6 = domingo
            raise serializers.ValidationError("Não atendemos aos domingos")
        
        return value

    def validate(self, data):
        """Validação cruzada de dados"""
        horario = data.get('horario')
        servico = data.get('servico')
        
        if horario and servico:
            # Verificar conflito de horários
            fim_agendamento = horario + timedelta(minutes=servico.duracao_minutos)
            
            conflitos = Agendamento.objects.filter(
                status='confirmado',
                horario__lt=fim_agendamento,
                horario__gte=horario - timedelta(minutes=servico.duracao_minutos)
            )
            
            if conflitos.exists():
                raise serializers.ValidationError({
                    'horario': 'Existe conflito de horário com outro agendamento'
                })
        
        return data


class AgendamentoDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para visualização de agendamentos"""
    
    cliente_nome = serializers.CharField(source='cliente.nome', read_only=True)
    cliente_whatsapp = serializers.CharField(source='cliente.whatsapp', read_only=True)
    servico_nome = serializers.CharField(source='servico.nome', read_only=True)
    servico_duracao = serializers.IntegerField(source='servico.duracao_minutos', read_only=True)
    horario_fim = serializers.ReadOnlyField()
    pode_cancelar = serializers.ReadOnlyField()
    esta_atrasado = serializers.ReadOnlyField()
    
    class Meta:
        model = Agendamento
        fields = [
            'id', 'cliente', 'cliente_nome', 'cliente_whatsapp',
            'servico', 'servico_nome', 'servico_duracao',
            'horario', 'horario_fim', 'status', 'observacoes',
            'valor_cobrado', 'criado_em', 'atualizado_em',
            'pode_cancelar', 'esta_atrasado'
        ]
        read_only_fields = ['criado_em', 'atualizado_em']


class AgendamentoUpdateSerializer(serializers.ModelSerializer):
    """Serializer específico para atualização de agendamentos"""
    
    class Meta:
        model = Agendamento
        fields = ['status', 'observacoes', 'valor_cobrado']

    def validate_status(self, value):
        """Validação para mudança de status"""
        if self.instance:
            status_atual = self.instance.status
            
            # Regras de transição de status
            transicoes_validas = {
                'confirmado': ['concluido', 'cancelado', 'reagendado', 'falta'],
                'reagendado': ['confirmado', 'cancelado'],
                'cancelado': [],  # Cancelado não pode mudar
                'concluido': [],  # Concluído não pode mudar
                'falta': ['reagendado']  # Falta pode ser reagendada
            }
            
            if value not in transicoes_validas.get(status_atual, []):
                raise serializers.ValidationError(
                    f"Não é possível mudar status de '{status_atual}' para '{value}'"
                )
        
        return value


class DashboardSerializer(serializers.Serializer):
    """Serializer para dados do dashboard"""
    
    agendamentos_hoje = serializers.IntegerField()
    agendamentos_semana = serializers.IntegerField()
    agendamentos_mes = serializers.IntegerField()
    receita_mes = serializers.DecimalField(max_digits=10, decimal_places=2)
    clientes_ativos = serializers.IntegerField()
    servicos_mais_procurados = serializers.ListField()
    proximos_agendamentos = AgendamentoDetailSerializer(many=True)


class CalendarioSerializer(serializers.Serializer):
    """Serializer para eventos do calendário"""
    
    id = serializers.IntegerField()
    title = serializers.CharField()
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    color = serializers.CharField()
    cliente = serializers.CharField()
    servico = serializers.CharField()
    status = serializers.CharField()
    observacoes = serializers.CharField()
