#!/usr/bin/env python3
"""
Ávila DevOps SaaS - Configuração Inicial para Clientes
Script para configurar ambiente inicial de forma automatizada
"""

import os
import sys
import json
import secrets
import subprocess
from pathlib import Path

# Adicionar diretório raiz ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def generate_secret_key():
    """Gerar chave secreta segura"""
    return secrets.token_urlsafe(50)

def create_env_file():
    """Criar arquivo .env com configurações básicas"""
    env_file = project_root / '.env'

    if env_file.exists():
        print("✅ Arquivo .env já existe. Pulando criação.")
        return

    # Coletar informações básicas
    print("🚀 Configuração Inicial - Ávila DevOps SaaS")
    print("=" * 50)
    print()

    company_name = input("Nome da empresa: ").strip()
    admin_email = input("Email do administrador: ").strip()

    while True:
        admin_password = input("Senha do administrador (mínimo 8 caracteres): ").strip()
        if len(admin_password) >= 8:
            break
        print("❌ Senha deve ter pelo menos 8 caracteres!")

    # Gerar configurações
    env_content = f"""# Ávila DevOps SaaS - Configuração do Cliente
# Gerado automaticamente em {os.times()}

# Informações da empresa
COMPANY_NAME="{company_name}"
ADMIN_EMAIL="{admin_email}"
ADMIN_PASSWORD="{admin_password}"

# Configurações de desenvolvimento local
ENVIRONMENT=development
DEBUG=True
SECRET_KEY={generate_secret_key()}

# Banco de dados (SQLite para desenvolvimento local)
DATABASE_URL=sqlite:///data/db.sqlite3

# Cache (opcional para desenvolvimento local)
REDIS_URL=redis://localhost:6379/0

# URLs da plataforma
LANDING_PAGE_URL=https://aviladevops.com.br
ADMIN_URL=https://admin.aviladevops.com.br

# Configurações de segurança (desenvolvimento)
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False

# Logging
LOG_LEVEL=INFO

# Configurações específicas do cliente
# (Estas podem ser personalizadas conforme necessidade)
MAX_USERS=100
STORAGE_LIMIT_GB=10
"""

    with open(env_file, 'w') as f:
        f.write(env_content)

    print("✅ Arquivo .env criado com sucesso!")

def setup_database():
    """Configurar banco de dados"""
    print("🗄️  Configurando banco de dados...")

    # Criar diretório de dados
    data_dir = project_root / 'data'
    data_dir.mkdir(exist_ok=True)

    # Executar migrações se Django estiver disponível
    try:
        import django
        from django.conf import settings
        from django.core.management import execute_from_command_line

        # Configurar Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

        # Executar migrações
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print("✅ Migrações executadas com sucesso!")

    except ImportError:
        print("⚠️  Django não encontrado. Execute 'pip install -r requirements.txt' primeiro.")
    except Exception as e:
        print(f"❌ Erro ao executar migrações: {e}")

def create_admin_user():
    """Criar usuário administrador"""
    print("👤 Criando usuário administrador...")

    try:
        import django
        from django.conf import settings
        from django.core.management import execute_from_command_line

        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

        # Executar comando para criar superusuário
        execute_from_command_line(['manage.py', 'create_admin_user', '--noinput'])
        print("✅ Usuário administrador criado com sucesso!")

    except Exception as e:
        print(f"❌ Erro ao criar usuário: {e}")

def collect_static_files():
    """Coletar arquivos estáticos"""
    print("📁 Coletando arquivos estáticos...")

    try:
        import django
        from django.conf import settings
        from django.core.management import execute_from_command_line

        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        print("✅ Arquivos estáticos coletados!")

    except Exception as e:
        print(f"❌ Erro ao coletar estáticos: {e}")

def test_configuration():
    """Testar configuração"""
    print("🧪 Testando configuração...")

    try:
        # Testar se consegue importar configurações
        from core.settings import SECRET_KEY, DEBUG

        print("✅ Configurações carregadas com sucesso!")
        print(f"   DEBUG: {DEBUG}")
        print(f"   SECRET_KEY: {SECRET_KEY[:20]}...")

        # Testar conexão com banco
        import django
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("✅ Banco de dados conectado!")

    except Exception as e:
        print(f"❌ Erro na configuração: {e}")
        return False

    return True

def show_completion_message():
    """Mostrar mensagem de conclusão"""
    print()
    print("🎉 CONFIGURAÇÃO INICIAL CONCLUÍDA!")
    print("=" * 50)
    print()

    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            content = f.read()

        # Extrair informações importantes
        for line in content.split('\n'):
            if line.startswith('COMPANY_NAME='):
                print(f"🏢 Empresa: {line.split('=', 1)[1].strip('\"')}")
            elif line.startswith('ADMIN_EMAIL='):
                print(f"📧 Email Admin: {line.split('=', 1)[1].strip('\"')}")

    print()
    print("📋 PRÓXIMOS PASSOS:")
    print("1. Execute: python manage.py runserver")
    print("2. Acesse: http://localhost:8000")
    print("3. Faça login com suas credenciais")
    print("4. Complete a configuração no admin")
    print()
    print("💡 DICAS:")
    print("• Para produção: docker-compose -f docker-compose.prod.yml up")
    print("• Para desenvolvimento: docker-compose -f docker-compose.dev.yml up")
    print("• Para monitoramento: python scripts/local_metrics.py")
    print()
    print("🛠️  SUPORTE:")
    print("• Documentação: https://docs.aviladevops.com.br")
    print("• Email: suporte@aviladevops.com.br")
    print("• WhatsApp: +55 17 99781-1471")

def main():
    print("🚀 Ávila DevOps SaaS - Configuração Inicial Automática")
    print("=" * 60)
    print()

    # Verificar se está no diretório correto
    if not (project_root / 'requirements.txt').exists():
        print("❌ Execute este script a partir do diretório raiz do projeto!")
        sys.exit(1)

    # Verificar se Python está disponível
    if not sys.executable:
        print("❌ Python não encontrado!")
        sys.exit(1)

    try:
        # Passo 1: Criar arquivo .env
        create_env_file()

        # Passo 2: Configurar banco de dados
        setup_database()

        # Passo 3: Coletar arquivos estáticos
        collect_static_files()

        # Passo 4: Testar configuração
        if test_configuration():
            show_completion_message()
        else:
            print("❌ Há problemas na configuração. Verifique os logs acima.")

    except KeyboardInterrupt:
        print("\n\n🛑 Configuração interrompida pelo usuário")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
