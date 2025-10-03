"""
Script de configuração inicial do sistema
Configura banco de dados, cria superusuário e testa conexões
"""

import os
import sys
import subprocess
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xml_manager.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.contrib.auth.models import User
from django.core.management import call_command


def print_header(text):
    """Imprime cabeçalho estilizado"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)


def run_migrations():
    """Executa as migrações do banco"""
    print_header("MIGRANDO BANCO DE DADOS")
    try:
        call_command('makemigrations')
        call_command('migrate')
        print("✓ Migrações concluídas com sucesso!")
        return True
    except Exception as e:
        print(f"✗ Erro ao migrar: {e}")
        return False


def create_superuser():
    """Cria superusuário se não existir"""
    print_header("CRIANDO SUPERUSUÁRIO")
    
    if User.objects.filter(username='admin').exists():
        print("✓ Superusuário 'admin' já existe")
        return True
    
    try:
        User.objects.create_superuser(
            username='admin',
            email='admin@xmlmanager.com',
            password='admin123'
        )
        print("✓ Superusuário criado com sucesso!")
        print("\n  Username: admin")
        print("  Password: admin123")
        print("\n  ⚠️  ALTERE A SENHA EM PRODUÇÃO!")
        return True
    except Exception as e:
        print(f"✗ Erro ao criar superusuário: {e}")
        return False


def collect_static():
    """Coleta arquivos estáticos"""
    print_header("COLETANDO ARQUIVOS ESTÁTICOS")
    try:
        call_command('collectstatic', '--noinput', '--clear')
        print("✓ Arquivos estáticos coletados!")
        return True
    except Exception as e:
        print(f"⚠️  Aviso: {e}")
        return True  # Não é crítico


def test_database():
    """Testa conexão com banco de dados"""
    print_header("TESTANDO BANCO DE DADOS")
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        print("✓ Conexão com banco de dados OK!")
        
        # Mostra informações do banco
        from django.conf import settings
        db = settings.DATABASES['default']
        print(f"\n  Engine: {db['ENGINE']}")
        if 'mysql' in db['ENGINE']:
            print(f"  Host: {db.get('HOST', 'localhost')}")
            print(f"  Database: {db.get('NAME', 'N/A')}")
        else:
            print(f"  Database: {db.get('NAME', 'SQLite')}")
        
        return True
    except Exception as e:
        print(f"✗ Erro de conexão: {e}")
        return False


def show_stats():
    """Mostra estatísticas do sistema"""
    print_header("ESTATÍSTICAS DO SISTEMA")
    try:
        from core.models import NFe, CTe, ImportLog
        
        nfe_count = NFe.objects.count()
        cte_count = CTe.objects.count()
        log_count = ImportLog.objects.count()
        user_count = User.objects.count()
        
        print(f"\n  📄 NFes: {nfe_count}")
        print(f"  🚚 CTes: {cte_count}")
        print(f"  📋 Logs: {log_count}")
        print(f"  👥 Usuários: {user_count}")
        
        return True
    except Exception as e:
        print(f"✗ Erro ao buscar estatísticas: {e}")
        return False


def show_urls():
    """Mostra URLs importantes"""
    print_header("ACESSO AO SISTEMA")
    print("\n  🌐 Web Interface:")
    print("     http://localhost:8000")
    print("\n  👤 Login:")
    print("     http://localhost:8000/login/")
    print("\n  🔧 Admin:")
    print("     http://localhost:8000/admin/")
    print("\n  📡 API REST:")
    print("     http://localhost:8000/api/")
    print("\n  📚 Documentação API:")
    print("     http://localhost:8000/api/nfe/")
    print("     http://localhost:8000/api/cte/")
    print("     http://localhost:8000/api/dashboard/")


def main():
    """Função principal"""
    print("\n" + "="*60)
    print("  🚀 XML MANAGER - SETUP INICIAL")
    print("="*60)
    
    steps = [
        ("Migrando banco de dados", run_migrations),
        ("Criando superusuário", create_superuser),
        ("Coletando estáticos", collect_static),
        ("Testando banco de dados", test_database),
        ("Verificando estatísticas", show_stats),
    ]
    
    success_count = 0
    for step_name, step_func in steps:
        if step_func():
            success_count += 1
    
    # Resultado final
    print_header("RESULTADO FINAL")
    print(f"\n  ✓ {success_count}/{len(steps)} etapas concluídas")
    
    if success_count == len(steps):
        print("\n  🎉 SETUP CONCLUÍDO COM SUCESSO!")
        show_urls()
        
        print_header("PRÓXIMOS PASSOS")
        print("\n  1. Inicie o servidor:")
        print("     python manage.py runserver")
        print("\n  2. Acesse o sistema:")
        print("     http://localhost:8000")
        print("\n  3. Faça login com:")
        print("     Usuário: admin")
        print("     Senha: admin123")
        print("\n  4. Para desenvolver app mobile:")
        print("     Consulte: web_app/README.md")
        print("\n  5. Para importar XMLs:")
        print("     Execute: python ../import_to_cloudsql.py")
    else:
        print("\n  ⚠️  SETUP CONCLUÍDO COM AVISOS")
        print("\n  Verifique os erros acima e tente novamente.")
    
    print("\n" + "="*60 + "\n")


if __name__ == '__main__':
    main()
