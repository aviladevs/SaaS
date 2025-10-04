#!/usr/bin/env python3
"""
Ávila DevOps SaaS - Admin Portal
Portal web simples para facilitar operações para funcionários
"""

import os
import json
import subprocess
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configurações
PROJECT_ROOT = Path(__file__).parent.parent
SERVICES = {
    'landing-page': {'name': 'Landing Page', 'url': 'https://aviladevops.com.br'},
    'sistema': {'name': 'Sistema Reciclagem', 'url': 'https://sistema.aviladevops.com.br'},
    'fiscal': {'name': 'Sistema Fiscal', 'url': 'https://fiscal.aviladevops.com.br'},
    'clinica': {'name': 'Clínica Management', 'url': 'https://clinica.aviladevops.com.br'},
    'app-aviladevops': {'name': 'Admin Dashboard', 'url': 'https://admin.aviladevops.com.br'}
}

@app.route('/')
def dashboard():
    """Dashboard principal"""
    return render_template('admin_dashboard.html', services=SERVICES)

@app.route('/deploy', methods=['GET', 'POST'])
def deploy():
    """Página de deploy"""
    if request.method == 'POST':
        service = request.form.get('service')
        environment = request.form.get('environment', 'production')

        try:
            if service == 'all':
                result = subprocess.run(['make', 'deploy-prod'], capture_output=True, text=True, cwd=PROJECT_ROOT)
            else:
                # Deploy específico do serviço
                result = subprocess.run(['make', f'deploy-{service}'], capture_output=True, text=True, cwd=PROJECT_ROOT)

            if result.returncode == 0:
                flash(f'Deploy do serviço {service} realizado com sucesso!', 'success')
            else:
                flash(f'Erro no deploy: {result.stderr}', 'error')

        except Exception as e:
            flash(f'Erro ao executar deploy: {str(e)}', 'error')

        return redirect(url_for('deploy'))

    return render_template('deploy.html', services=SERVICES)

@app.route('/tenants', methods=['GET', 'POST'])
def tenants():
    """Gestão de tenants"""
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'create':
            tenant_name = request.form.get('tenant_name')
            tenant_domain = request.form.get('tenant_domain')
            admin_email = request.form.get('admin_email')

            try:
                result = subprocess.run([
                    'python', 'scripts/tenant_management.py', 'create',
                    '--name', tenant_name,
                    '--domain', tenant_domain,
                    '--owner-email', admin_email
                ], capture_output=True, text=True, cwd=PROJECT_ROOT)

                if result.returncode == 0:
                    flash(f'Tenant {tenant_name} criado com sucesso!', 'success')
                else:
                    flash(f'Erro ao criar tenant: {result.stderr}', 'error')

            except Exception as e:
                flash(f'Erro: {str(e)}', 'error')

        elif action == 'list':
            # Listar tenants
            pass

    return render_template('tenants.html')

@app.route('/monitoring')
def monitoring():
    """Página de monitoramento"""
    # Coletar métricas básicas
    metrics = {
        'uptime': get_uptime(),
        'memory': get_memory_usage(),
        'disk': get_disk_usage(),
        'services': get_service_status()
    }

    return render_template('monitoring.html', metrics=metrics)

@app.route('/api/health')
def api_health():
    """API health check"""
    return {'status': 'healthy', 'timestamp': str(os.times())}

def get_uptime():
    """Obter uptime do sistema"""
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            return str(int(uptime_seconds // 3600)) + 'h ' + str(int((uptime_seconds % 3600) // 60)) + 'm'
    except:
        return 'N/A'

def get_memory_usage():
    """Obter uso de memória"""
    try:
        with open('/proc/meminfo', 'r') as f:
            lines = f.readlines()
            total = int(lines[0].split()[1])
            available = int(lines[2].split()[1])
            used = total - available
            return f'{used * 100 / total:.1f}%'
    except:
        return 'N/A'

def get_disk_usage():
    """Obter uso de disco"""
    try:
        result = subprocess.run(['df', '/'], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')
        return lines[-1].split()[4]  # Percentual usado
    except:
        return 'N/A'

def get_service_status():
    """Obter status dos serviços"""
    status = {}
    for service_id, service_info in SERVICES.items():
        # Verificar se serviço está respondendo
        try:
            import requests
            response = requests.get(f"{service_info['url']}/health/", timeout=5)
            status[service_id] = 'healthy' if response.status_code == 200 else 'error'
        except:
            status[service_id] = 'unknown'

    return status

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
