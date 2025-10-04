#!/usr/bin/env python3
"""
Script de deploy atualizado para Google Cloud
Corrige problemas de Dockerfile e estrutura de projetos
"""
import os
import subprocess
import sys

def run_command(cmd, cwd=None):
    """Executa comando e retorna resultado"""
    print(f"🔧 Executando: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.stdout:
            print(f"📋 Output: {result.stdout}")
        if result.stderr:
            print(f"⚠️  Warning: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def check_dockerfile(service_path):
    """Verifica se o Dockerfile existe e é válido"""
    dockerfile_path = os.path.join(service_path, "Dockerfile")
    if os.path.exists(dockerfile_path):
        print(f"✅ Dockerfile encontrado em: {dockerfile_path}")
        return True
    else:
        print(f"❌ Dockerfile não encontrado em: {dockerfile_path}")
        return False

def deploy_service(service_name, source_path, port=8080, use_dockerfile=True):
    """Faz deploy de um serviço específico"""
    print(f"\n🚀 Fazendo deploy do serviço: {service_name}")
    print(f"📁 Source: {source_path}")

    # Verificar se Dockerfile existe
    if use_dockerfile and not check_dockerfile(source_path):
        print(f"⚠️ Pulando deploy de {service_name} - Dockerfile não encontrado")
        return False

    # Deploy usando gcloud run
    if use_dockerfile:
        cmd = f"gcloud run deploy {service_name} --source {source_path} --platform managed --region southamerica-east1 --allow-unauthenticated --port {port}"
    else:
        # Para serviços sem Dockerfile, usar buildpacks
        cmd = f"gcloud run deploy {service_name} --source {source_path} --platform managed --region southamerica-east1 --allow-unauthenticated"

    success = run_command(cmd)
    if success:
        print(f"✅ Serviço {service_name} deployado com sucesso!")
        return True
    else:
        print(f"❌ Falha no deploy do serviço {service_name}")
        return False

def main():
    """Função principal"""
    print("🚀 Iniciando deploy dos serviços SaaS...")

    # Lista de serviços para deploy
    services = [
        ("landing-page", "LANDING-PAGE", 8080, True),
        ("sistema", "sistema", 8000, True),
        ("fiscal", "fiscal/web_app", 8000, True),
        ("clinica", "clinica", 3000, True),
    ]

    success_count = 0

    for service_name, source_path, port, use_dockerfile in services:
        if deploy_service(service_name, source_path, port, use_dockerfile):
            success_count += 1

    print(f"\n📊 Deploy concluído: {success_count}/{len(services)} serviços deployados com sucesso")

    if success_count == len(services):
        print("🎉 Todos os serviços foram deployados com sucesso!")
        return True
    else:
        print("⚠️ Alguns serviços falharam no deploy")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
