"""
Script para inicializar banco de dados no Cloud
Execute via SSH na instância do App Engine
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xml_manager.settings_production')
django.setup()

from django.core.management import call_command
from django.contrib.auth.models import User

print("="*60)
print("  INICIALIZANDO BANCO DE DADOS")
print("="*60)

# Executar migrações
print("\n[1/3] Executando migrações...")
try:
    call_command('migrate', '--noinput')
    print("✅ Migrações concluídas!")
except Exception as e:
    print(f"❌ Erro nas migrações: {e}")

# Criar superusuário se não existir
print("\n[2/3] Criando superusuário...")
try:
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@aviladevops.com.br',
            password='Admin@2025'
        )
        print("✅ Superusuário criado!")
        print("\n  Username: admin")
        print("  Password: Admin@2025")
        print("\n  ⚠️  ALTERE A SENHA EM PRODUÇÃO!")
    else:
        print("✅ Superusuário já existe!")
except Exception as e:
    print(f"❌ Erro ao criar superusuário: {e}")

# Coletar estáticos
print("\n[3/3] Coletando arquivos estáticos...")
try:
    call_command('collectstatic', '--noinput', '--clear')
    print("✅ Estáticos coletados!")
except Exception as e:
    print(f"⚠️  Aviso: {e}")

print("\n" + "="*60)
print("  ✅ INICIALIZAÇÃO CONCLUÍDA!")
print("="*60)
print("\n🌐 Acesse: https://nicolasrosaab.rj.r.appspot.com")
print("🔑 Login: admin / Admin@2025")
print("\n")
