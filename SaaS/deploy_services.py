#!/usr/bin/env python3
"""
Script de deploy simplificado para Google Cloud
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

def deploy_service(service_name, source_path, port=8080):
    """Faz deploy de um serviço específico"""
    print(f"\n🚀 Fazendo deploy do serviço: {service_name}")
    print(f"📁 Source: {source_path}")

    # Build e deploy usando gcloud run
    cmd = f"gcloud run deploy {service_name} --source {source_path} --platform managed --region southamerica-east1 --allow-unauthenticated --port {port}"

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
        ("landing-page", "LANDING-PAGE", 8080),
        ("sistema", "sistema", 8000),
        ("fiscal", "fiscal/web_app", 8000),
        ("clinica", "clinica", 3000),
    ]

    success_count = 0

    for service_name, source_path, port in services:
        if deploy_service(service_name, source_path, port):
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
