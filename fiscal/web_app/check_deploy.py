"""
Script de verificação pré-deploy
Verifica se tudo está pronto para deploy no GCP

Uso:
    python check_deploy.py              # Modo interativo (espera ENTER no final)
    python check_deploy.py --no-prompt  # Modo não-interativo (para CI/automação)

Códigos de saída:
    0 - Tudo pronto para deploy
    1 - Quase pronto (com avisos)
    2 - Não está pronto (com erros)
"""

import os
import sys
import subprocess
from pathlib import Path


def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)


def check_gcloud():
    """Verifica se gcloud está instalado"""
    print_header("VERIFICANDO GOOGLE CLOUD SDK")
    try:
        result = subprocess.run(['gcloud', '--version'], 
                              capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            print("✅ Google Cloud SDK instalado")
            print(result.stdout.split('\n')[0])
            return True
        else:
            print("❌ Google Cloud SDK não funciona corretamente")
            return False
    except FileNotFoundError:
        print("❌ Google Cloud SDK NÃO instalado")
        print("\n💡 Instale em: https://cloud.google.com/sdk/docs/install")
        return False
    except subprocess.TimeoutExpired:
        print("⚠️  Google Cloud SDK não responde (timeout)")
        print("\n💡 Verifique se o gcloud está instalado corretamente")
        return False
    except Exception as e:
        print(f"❌ Erro ao verificar gcloud: {e}")
        return False


def check_authenticated():
    """Verifica se está autenticado"""
    print_header("VERIFICANDO AUTENTICAÇÃO")
    try:
        result = subprocess.run(['gcloud', 'auth', 'list'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and 'ACTIVE' in result.stdout:
            print("✅ Autenticado no Google Cloud")
            return True
        else:
            print("❌ NÃO autenticado")
            print("\n💡 Execute: gcloud auth login")
            return False
    except subprocess.TimeoutExpired:
        print("⚠️  Comando de autenticação não responde (timeout)")
        print("\n💡 Execute: gcloud auth login")
        return False
    except FileNotFoundError:
        print("⚠️  Google Cloud SDK não encontrado")
        print("\n💡 Instale o gcloud primeiro")
        return False
    except Exception as e:
        print(f"❌ Erro ao verificar autenticação: {e}")
        return False


def check_project():
    """Verifica se projeto está configurado"""
    print_header("VERIFICANDO PROJETO")
    try:
        result = subprocess.run(['gcloud', 'config', 'get-value', 'project'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip() and result.stdout.strip() != '(unset)':
            project = result.stdout.strip()
            print(f"✅ Projeto configurado: {project}")
            return True
        else:
            print("❌ Projeto NÃO configurado")
            print("\n💡 Execute:")
            print("   gcloud projects list")
            print("   gcloud config set project SEU_PROJECT_ID")
            return False
    except subprocess.TimeoutExpired:
        print("⚠️  Comando não responde (timeout)")
        print("\n💡 Verifique a instalação do gcloud")
        return False
    except FileNotFoundError:
        print("⚠️  Google Cloud SDK não encontrado")
        return False
    except Exception as e:
        print(f"❌ Erro ao verificar projeto: {e}")
        return False


def check_files():
    """Verifica se arquivos necessários existem"""
    print_header("VERIFICANDO ARQUIVOS")
    
    required_files = {
        'app.yaml': 'Configuração App Engine',
        'requirements.txt': 'Dependências Python',
        'manage.py': 'Django management',
        'xml_manager/settings.py': 'Settings Django',
        'xml_manager/settings_production.py': 'Settings produção',
    }
    
    all_ok = True
    for file, desc in required_files.items():
        if Path(file).exists():
            print(f"✅ {file:<35} - {desc}")
        else:
            print(f"❌ {file:<35} - FALTANDO!")
            all_ok = False
    
    return all_ok


def check_staticfiles():
    """Verifica se static files foram coletados"""
    print_header("VERIFICANDO ARQUIVOS ESTÁTICOS")
    
    static_dir = Path('staticfiles')
    if static_dir.exists() and list(static_dir.iterdir()):
        print(f"✅ Arquivos estáticos coletados ({len(list(static_dir.rglob('*')))} arquivos)")
        return True
    else:
        print("⚠️  Arquivos estáticos NÃO coletados")
        print("\n💡 Execute:")
        print("   python manage.py collectstatic --noinput")
        return False


def check_app_engine():
    """Verifica se App Engine existe"""
    print_header("VERIFICANDO APP ENGINE")
    try:
        result = subprocess.run(['gcloud', 'app', 'describe'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ App Engine já configurado")
            return True
        else:
            print("⚠️  App Engine NÃO criado")
            print("\n💡 Execute (APENAS UMA VEZ):")
            print("   gcloud app create --region=southamerica-east1")
            return False
    except subprocess.TimeoutExpired:
        print("⚠️  Comando não responde (timeout)")
        print("\n💡 Verifique a instalação do gcloud")
        return False
    except FileNotFoundError:
        print("⚠️  Google Cloud SDK não encontrado")
        return False
    except Exception as e:
        print(f"❌ Erro ao verificar App Engine: {e}")
        return False


def show_deploy_command():
    """Mostra comandos para deploy"""
    print_header("COMANDOS PARA DEPLOY")
    print("\n📋 Se tudo estiver OK, execute:")
    print("\n1️⃣ Coletar estáticos (se ainda não fez):")
    print("   python manage.py collectstatic --noinput")
    print("\n2️⃣ Deploy:")
    print("   gcloud app deploy app.yaml --quiet")
    print("\n3️⃣ Abrir app:")
    print("   gcloud app browse")
    print("\n4️⃣ Ver logs:")
    print("   gcloud app logs tail -s default")


def main():
    print("\n" + "="*60)
    print("  🚀 VERIFICAÇÃO PRÉ-DEPLOY - XML MANAGER")
    print("="*60)
    
    checks = [
        ("Google Cloud SDK", check_gcloud),
        ("Autenticação", check_authenticated),
        ("Projeto GCP", check_project),
        ("Arquivos necessários", check_files),
        ("Arquivos estáticos", check_staticfiles),
        ("App Engine", check_app_engine),
    ]
    
    results = []
    for name, check_func in checks:
        results.append(check_func())
    
    # Resultado final
    print_header("RESULTADO FINAL")
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n✅ Verificações passadas: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 TUDO PRONTO PARA DEPLOY!")
        show_deploy_command()
        return 0  # Success
    elif passed >= total - 1:
        print("\n⚠️  QUASE PRONTO! Corrija os avisos acima.")
        show_deploy_command()
        return 1  # Warning
    else:
        print("\n❌ AINDA NÃO ESTÁ PRONTO")
        print("\nCorrija os erros acima antes de fazer deploy.")
        print("\n📚 Consulte: DEPLOY_RAPIDO.md ou DEPLOY.md")
        return 2  # Error
    
    print("\n" + "="*60 + "\n")


if __name__ == '__main__':
    exit_code = main()
    # Only wait for input if not running non-interactively
    # Check if running in CI or with --no-prompt flag
    if '--no-prompt' not in sys.argv and sys.stdin.isatty():
        input("Pressione ENTER para sair...")
    sys.exit(exit_code if exit_code is not None else 0)

