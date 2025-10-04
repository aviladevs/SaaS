# 🚀 Guia de Início Rápido - Sistema de Integrações

Este guia mostra como começar a usar o sistema de integrações e automações em poucos minutos.

---

## 📦 Instalação

### 1. Instalar Dependências

```bash
cd fiscal/web_app
pip install -r requirements.txt
```

### 2. Configurar Banco de Dados

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 3. Iniciar Servidor

```bash
python manage.py runserver
```

---

## 🔑 Obter Token de API

1. Faça login no sistema: `http://localhost:8000/admin/`
2. Crie um token em: **Auth Token** > **Add Token**
3. Copie o token gerado

Ou via API:

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "sua-senha"}'
```

Resposta:
```json
{
  "token": "seu-token-aqui"
}
```

---

## 🔗 Criar Seu Primeiro Webhook

### Via API

```bash
curl -X POST http://localhost:8000/api/webhooks/ \
  -H "Authorization: Token SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Meu Primeiro Webhook",
    "url": "https://webhook.site/seu-uuid",
    "eventos": "nfe_importada,cte_importado",
    "ativo": true,
    "timeout": 30,
    "retry_count": 3
  }'
```

### Via Python

```python
from fiscal_api_client import FiscalAPIClient

client = FiscalAPIClient('http://localhost:8000', 'SEU_TOKEN')

webhook = client.criar_webhook(
    nome='Meu Primeiro Webhook',
    url='https://webhook.site/seu-uuid',
    eventos='nfe_importada,cte_importado',
    ativo=True
)

print(f"✓ Webhook criado: ID {webhook['id']}")
```

---

## 🧪 Testar Webhook

```bash
curl -X POST http://localhost:8000/api/webhooks/1/testar/ \
  -H "Authorization: Token SEU_TOKEN"
```

Ou via Python:

```python
resultado = client.testar_webhook(webhook['id'])
print(resultado['mensagem'])
```

---

## 📊 Monitorar Webhooks

### Ver Estatísticas

```bash
curl http://localhost:8000/api/webhooks/estatisticas/ \
  -H "Authorization: Token SEU_TOKEN"
```

### Ver Logs

```bash
curl http://localhost:8000/api/webhooks/1/logs/ \
  -H "Authorization: Token SEU_TOKEN"
```

---

## ⏰ Configurar Tarefas Agendadas

### 1. Executar Manualmente

```bash
# Todas as tarefas
python manage.py run_scheduled_tasks

# Apenas consultas SEFAZ
python manage.py run_scheduled_tasks --task=consultas_sefaz

# Apenas limpeza de logs
python manage.py run_scheduled_tasks --task=limpeza_logs

# Apenas relatórios
python manage.py run_scheduled_tasks --task=enviar_relatorios
```

### 2. Agendar com Cron

Edite o crontab:

```bash
crontab -e
```

Adicione:

```cron
# Consultas SEFAZ a cada 30 minutos
*/30 * * * * cd /path/to/fiscal/web_app && python manage.py run_scheduled_tasks --task=consultas_sefaz

# Limpeza de logs às 2h da manhã
0 2 * * * cd /path/to/fiscal/web_app && python manage.py run_scheduled_tasks --task=limpeza_logs

# Relatórios diários às 8h
0 8 * * * cd /path/to/fiscal/web_app && python manage.py run_scheduled_tasks --task=enviar_relatorios
```

### 3. Agendar com Systemd (Linux)

Crie `/etc/systemd/system/fiscal-tasks.service`:

```ini
[Unit]
Description=Fiscal Tasks Runner
After=network.target

[Service]
Type=oneshot
User=www-data
WorkingDirectory=/path/to/fiscal/web_app
ExecStart=/usr/bin/python manage.py run_scheduled_tasks
```

Crie `/etc/systemd/system/fiscal-tasks.timer`:

```ini
[Unit]
Description=Run Fiscal Tasks Hourly

[Timer]
OnCalendar=hourly
Persistent=true

[Install]
WantedBy=timers.target
```

Ative:

```bash
sudo systemctl enable fiscal-tasks.timer
sudo systemctl start fiscal-tasks.timer
```

---

## 📱 Usar Cliente Python

### Instalação

```python
# Copie o arquivo fiscal_api_client.py para seu projeto
from fiscal_api_client import FiscalAPIClient

# Configure
client = FiscalAPIClient('http://localhost:8000', 'SEU_TOKEN')
```

### Listar NFes

```python
nfes = client.listar_nfes(search='empresa', limit=10)
print(f"Total: {nfes['count']} NFes")

for nfe in nfes['results']:
    print(f"NFe {nfe['numero_nf']} - {nfe['emit_nome']}")
```

### Dashboard

```python
dashboard = client.dashboard()
print(f"NFes: {dashboard['nfe_total']}")
print(f"CTes: {dashboard['cte_total']}")
print(f"Valor total NFe: R$ {dashboard['nfe_valor_total']}")
```

### Estatísticas

```python
stats = client.estatisticas()

print("Top 5 Emitentes:")
for emitente in stats['top_emitentes'][:5]:
    print(f"  {emitente['emit_nome']}: {emitente['total']} NFes")
```

### Busca

```python
resultados = client.buscar('12345')
print(f"NFes encontradas: {len(resultados['nfes'])}")
print(f"CTes encontrados: {len(resultados['ctes'])}")
```

---

## 🔌 Integração com Outros Serviços

### Exemplo 1: Integrar com Sistema Externo

```python
from fiscal_api_client import FiscalAPIClient

# Configuração
FISCAL_API = 'http://localhost:8000'
FISCAL_TOKEN = 'seu-token'

# Cliente
fiscal = FiscalAPIClient(FISCAL_API, FISCAL_TOKEN)

# Criar webhook apontando para seu sistema
webhook = fiscal.criar_webhook(
    nome='Integração ERP',
    url='https://meu-erp.com/webhook/fiscal',
    eventos='nfe_importada,cte_importado',
    secret_key='chave-secreta-compartilhada'
)

print(f"✓ Webhook criado: {webhook['id']}")

# Testar
resultado = fiscal.testar_webhook(webhook['id'])
print(f"Teste: {resultado['status']}")
```

### Exemplo 2: Sincronização Automática

```python
# sync_fiscal.py
import time
from fiscal_api_client import FiscalAPIClient

def sincronizar_nfes():
    """Sincroniza NFes do fiscal para outro sistema"""
    fiscal = FiscalAPIClient('http://localhost:8000', 'SEU_TOKEN')
    
    # Busca NFes recentes
    nfes = fiscal.listar_nfes(limit=50)
    
    for nfe in nfes['results']:
        # Processa cada NFe
        print(f"Processando NFe {nfe['numero_nf']}...")
        
        # Aqui você integraria com seu sistema
        # erp.importar_nfe(nfe)
        
        time.sleep(0.1)  # Evita sobrecarga

if __name__ == '__main__':
    sincronizar_nfes()
```

### Exemplo 3: Monitoramento

```python
# monitor.py
from fiscal_api_client import FiscalAPIClient
import time

def monitorar_sistema():
    """Monitora saúde do sistema fiscal"""
    fiscal = FiscalAPIClient('http://localhost:8000', 'SEU_TOKEN')
    
    while True:
        try:
            # Estatísticas de webhooks
            stats = fiscal.estatisticas_webhooks()
            
            taxa_sucesso = stats['taxa_sucesso']
            
            if taxa_sucesso < 90:
                print(f"⚠️ ALERTA: Taxa de sucesso baixa: {taxa_sucesso}%")
                # Envia alerta
            else:
                print(f"✓ Sistema OK: {taxa_sucesso}% de sucesso")
            
            # Aguarda 5 minutos
            time.sleep(300)
            
        except Exception as e:
            print(f"❌ Erro no monitoramento: {str(e)}")
            time.sleep(60)

if __name__ == '__main__':
    monitorar_sistema()
```

---

## 🎯 Exemplos de Uso Comum

### Receber Notificação no Slack

```python
# slack_notifier.py
from flask import Flask, request
import requests
import hmac
import hashlib

app = Flask(__name__)
SECRET_KEY = 'sua-chave-secreta'
SLACK_WEBHOOK = 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'

@app.route('/webhook/fiscal', methods=['POST'])
def webhook_fiscal():
    # Valida assinatura
    signature = request.headers.get('X-Webhook-Signature')
    payload = request.data.decode('utf-8')
    
    expected = hmac.new(
        SECRET_KEY.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected):
        return {'error': 'Invalid signature'}, 401
    
    # Processa evento
    data = request.json
    evento = data['evento']
    
    if evento == 'nfe_importada':
        nfe = data['dados']
        mensagem = f"✅ Nova NFe: {nfe['numero_nf']} - {nfe['emit_nome']} - R$ {nfe['valor_total']}"
        
        # Envia para Slack
        requests.post(SLACK_WEBHOOK, json={'text': mensagem})
    
    return {'status': 'ok'}

if __name__ == '__main__':
    app.run(port=5000)
```

### Exportar para Google Sheets

```python
# google_sheets_sync.py
from fiscal_api_client import FiscalAPIClient
from googleapiclient.discovery import build
from google.oauth2 import service_account

# Configuração
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'credentials.json'
SPREADSHEET_ID = 'your-spreadsheet-id'

def exportar_nfes_para_sheets():
    """Exporta NFes para Google Sheets"""
    
    # Cliente Fiscal
    fiscal = FiscalAPIClient('http://localhost:8000', 'SEU_TOKEN')
    
    # Cliente Google Sheets
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=credentials)
    
    # Busca NFes
    nfes = fiscal.listar_nfes(limit=100)
    
    # Prepara dados
    values = [['Número', 'Data', 'Emitente', 'Destinatário', 'Valor']]
    
    for nfe in nfes['results']:
        values.append([
            nfe['numero_nf'],
            nfe['data_emissao'],
            nfe['emit_nome'],
            nfe['dest_nome'],
            nfe['valor_total']
        ])
    
    # Atualiza planilha
    body = {'values': values}
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range='NFes!A1',
        valueInputOption='USER_ENTERED',
        body=body
    ).execute()
    
    print(f"✓ {len(values)-1} NFes exportadas para Google Sheets")

if __name__ == '__main__':
    exportar_nfes_para_sheets()
```

---

## 📞 Suporte

- **Documentação completa**: `INTEGRACOES.md`
- **Exemplos**: Veja pasta `exemplos/`
- **API Reference**: http://localhost:8000/api/

---

**🚀 Pronto para integrar!**
