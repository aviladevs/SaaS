"""
Testes completos para o sistema de agendamentos da clínica
Cobertura mínima para garantir funcionalidade crítica
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import datetime, timedelta
from .models import Cliente, Servico, Agendamento


class ClienteModelTest(TestCase):
    """Testes para o modelo Cliente"""

    def setUp(self):
        self.cliente = Cliente.objects.create(
            nome="João Silva",
            telefone="11999999999",
            email="joao@email.com"
        )

    def test_cliente_creation(self):
        """Testa criação do cliente"""
        self.assertEqual(self.cliente.nome, "João Silva")
        self.assertEqual(self.cliente.telefone, "11999999999")
        self.assertEqual(self.cliente.email, "joao@email.com")
        self.assertTrue(self.cliente.ativo)

    def test_cliente_str(self):
        """Testa representação string do cliente"""
        self.assertEqual(str(self.cliente), "João Silva")


class AgendamentoAPITest(APITestCase):
    """Testes para a API de agendamentos"""

    def setUp(self):
        self.cliente = Cliente.objects.create(
            nome="Pedro Costa",
            telefone="11777777777",
            email="pedro@email.com"
        )
        self.servico = Servico.objects.create(
            nome="Reflexologia",
            duracao=45,
            preco=60.00
        )

    def test_list_agendamentos(self):
        """Testa listagem de agendamentos"""
        Agendamento.objects.create(
            cliente=self.cliente,
            servico=self.servico,
            horario=datetime.now() + timedelta(days=1)
        )
        
        url = '/api/agendamentos/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_agendamento(self):
        """Testa criação de agendamento via API"""
        url = '/api/agendamentos/'
        data = {
            'cliente': self.cliente.id,
            'servico': self.servico.id,
            'horario': (datetime.now() + timedelta(days=2)).isoformat(),
            'observacoes': 'Teste API'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Agendamento.objects.count(), 1)
