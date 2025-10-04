#!/usr/bin/env python3
"""
Ávila DevOps SaaS - Métricas Locais para Clientes
Script para monitoramento de métricas locais e diagnóstico
"""

import os
import sys
import time
import psutil
import platform
import subprocess
from datetime import datetime
from pathlib import Path

# Adicionar diretório raiz ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def get_system_info():
    """Obter informações do sistema"""
    return {
        'platform': platform.platform(),
        'processor': platform.processor(),
        'architecture': platform.architecture(),
        'python_version': sys.version,
        'hostname': platform.node()
    }

def get_memory_usage():
    """Obter uso de memória"""
    memory = psutil.virtual_memory()
    return {
        'total': memory.total,
        'available': memory.available,
        'used': memory.used,
        'percentage': memory.percent
    }

def get_disk_usage():
    """Obter uso de disco"""
    disk = psutil.disk_usage('/')
    return {
        'total': disk.total,
        'free': disk.free,
        'used': disk.used,
        'percentage': disk.percent
    }

def get_network_info():
    """Obter informações de rede"""
    try:
        net = psutil.net_if_addrs()
        return {
            'interfaces': len(net),
            'addresses': [addr.address for interface in net.values() for addr in interface if addr.family.name == 'AF_INET']
        }
    except:
        return {'interfaces': 0, 'addresses': []}

def get_process_info():
    """Obter informações de processos"""
    try:
        # Verificar se há processos Django rodando
        django_processes = 0
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline'] and 'python' in proc.info['cmdline'][0]:
                    if any('manage.py' in cmd or 'gunicorn' in cmd for cmd in proc.info['cmdline']):
                        django_processes += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        return {
            'total_processes': len(list(psutil.process_iter())),
            'django_processes': django_processes,
            'cpu_percent': psutil.cpu_percent(interval=1)
        }
    except:
        return {'total_processes': 0, 'django_processes': 0, 'cpu_percent': 0}

def check_service_health():
    """Verificar saúde dos serviços"""
    services = {
        'database': False,
        'redis': False,
        'web_server': False
    }

    # Verificar banco de dados
    try:
        # Tentar conectar com SQLite (arquivo existe)
        if os.path.exists('db.sqlite3'):
            services['database'] = True
    except:
        pass

    # Verificar Redis (porta 6379)
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', 6379))
        sock.close()
        if result == 0:
            services['redis'] = True
    except:
        pass

    # Verificar servidor web (porta 8000)
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', 8000))
        sock.close()
        if result == 0:
            services['web_server'] = True
    except:
        pass

    return services

def show_metrics():
    """Mostrar métricas formatadas"""
    print("📊 MÉTRICAS LOCAIS - Ávila DevOps SaaS")
    print("=" * 50)
    print()

    # Sistema
    print("🖥️  SISTEMA:")
    sys_info = get_system_info()
    print(f"   Plataforma: {sys_info['platform']}")
    print(f"   Processador: {sys_info['processor']}")
    print(f"   Python: {sys_info['python_version'].split()[0]}")
    print()

    # Memória
    print("🧠 MEMÓRIA:")
    mem = get_memory_usage()
    print(f"   Total: {mem['total'] // (1024**3)".1f"} GB")
    print(f"   Usada: {mem['used'] // (1024**3)".1f"} GB ({mem['percentage']:.1".1f"")
    print(f"   Disponível: {mem['available'] // (1024**3)".1f"} GB")
    print()

    # Disco
    print("💾 DISCO:")
    disk = get_disk_usage()
    print(f"   Total: {disk['total'] // (1024**3)".1f"} GB")
    print(f"   Usado: {disk['used'] // (1024**3)".1f"} GB ({disk['percentage']:.1".1f"")
    print(f"   Livre: {disk['free'] // (1024**3)".1f"} GB")
    print()

    # Rede
    print("🌐 REDE:")
    net = get_network_info()
    print(f"   Interfaces: {net['interfaces']}")
    if net['addresses']:
        print(f"   Endereços IP: {', '.join(net['addresses'][:2])}")
    print()

    # Processos
    print("⚙️  PROCESSOS:")
    proc = get_process_info()
    print(f"   Total: {proc['total_processes']}")
    print(f"   Django: {proc['django_processes']}")
    print(f"   CPU: {proc['cpu_percent']:.1".1f")
    print()

    # Serviços
    print("🔧 SERVIÇOS:")
    services = check_service_health()
    for service, status in services.items():
        icon = "✅" if status else "❌"
        status_text = "OK" if status else "Indisponível"
        print(f"   {icon} {service.replace('_', ' ').title()}: {status_text}")
    print()

def export_metrics():
    """Exportar métricas para arquivo JSON"""
    timestamp = datetime.now().isoformat()

    metrics = {
        'timestamp': timestamp,
        'system': get_system_info(),
        'memory': get_memory_usage(),
        'disk': get_disk_usage(),
        'network': get_network_info(),
        'processes': get_process_info(),
        'services': check_service_health()
    }

    # Criar diretório de métricas se não existir
    metrics_dir = project_root / 'metrics'
    metrics_dir.mkdir(exist_ok=True)

    # Salvar métricas
    metrics_file = metrics_dir / f'metrics_{timestamp.replace(":", "-")}.json'
    with open(metrics_file, 'w') as f:
        import json
        json.dump(metrics, f, indent=2, default=str)

    print(f"✅ Métricas exportadas para: {metrics_file}")

def monitor_continuously():
    """Monitorar continuamente"""
    print("🔄 Iniciando monitoramento contínuo (Ctrl+C para parar)")
    print()

    try:
        while True:
            os.system('clear' if os.name == 'posix' else 'cls')
            show_metrics()
            print(f"\n🔄 Próxima atualização em 30 segundos...")
            time.sleep(30)
    except KeyboardInterrupt:
        print("\n\n🛑 Monitoramento interrompido pelo usuário")

def main():
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'export':
            export_metrics()
        elif command == 'monitor':
            monitor_continuously()
        else:
            print("Uso: python local_metrics.py [export|monitor]")
            sys.exit(1)
    else:
        show_metrics()

if __name__ == '__main__':
    main()
