#!/usr/bin/env python3
"""
Script simples para verificar se tudo está pronto para deploy no GCloud
Responde à pergunta: "Tudo certo para fazer o deploy no gcloud?"

Uso:
    python verificar_deploy.py
    
Este script executa check_deploy.py e fornece uma resposta clara sim/não.
"""

import sys
import subprocess
from pathlib import Path


def main():
    print("\n" + "="*70)
    print("  ❓ TUDO CERTO PARA FAZER O DEPLOY NO GCLOUD?")
    print("="*70 + "\n")
    
    # Executar check_deploy.py
    check_script = Path(__file__).parent / "check_deploy.py"
    
    if not check_script.exists():
        print("❌ Erro: check_deploy.py não encontrado!")
        print(f"   Procurado em: {check_script}")
        return 1
    
    try:
        # Executar o script de verificação
        result = subprocess.run(
            [sys.executable, str(check_script), "--no-prompt"],
            capture_output=False,
            text=True
        )
        
        print("\n" + "="*70)
        print("  📊 RESPOSTA FINAL")
        print("="*70 + "\n")
        
        if result.returncode == 0:
            print("✅ SIM! Tudo certo para fazer o deploy!")
            print("\n📝 Próximos passos:")
            print("   1. python manage.py collectstatic --noinput")
            print("   2. gcloud app deploy app.yaml --quiet")
            print("   3. gcloud app browse")
            return 0
            
        elif result.returncode == 1:
            print("⚠️  QUASE! Apenas alguns avisos.")
            print("\n💡 Você pode fazer o deploy, mas recomendamos:")
            print("   - Verificar os avisos acima")
            print("   - Coletar arquivos estáticos se necessário")
            print("\n📝 Se quiser prosseguir:")
            print("   1. python manage.py collectstatic --noinput")
            print("   2. gcloud app deploy app.yaml --quiet")
            return 1
            
        else:  # returncode == 2
            print("❌ NÃO! Ainda não está pronto.")
            print("\n💡 Corrija os erros indicados acima antes de fazer deploy.")
            print("\n📚 Consulte a documentação:")
            print("   - DEPLOY_RAPIDO.md - Para deploy rápido")
            print("   - DEPLOY_COMPLETO.md - Para instruções detalhadas")
            print("   - DEPLOY.md - Para configurações avançadas")
            return 2
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Verificação interrompida pelo usuário.")
        return 130
    except Exception as e:
        print(f"\n❌ Erro ao executar verificação: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
