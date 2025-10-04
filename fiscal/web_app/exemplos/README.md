# 📚 Exemplos de Integração

Esta pasta contém exemplos práticos de integração com o Sistema Fiscal.

---

## 📋 Exemplos Disponíveis

### 1. `webhook_receiver.py`

**Servidor Flask que recebe webhooks do Sistema Fiscal**

- Recebe notificações em tempo real
- Valida assinaturas HMAC
- Processa diferentes tipos de eventos
- Lista eventos recebidos

**Como usar:**

```bash
# Instalar dependências
pip install flask requests

# Executar
python webhook_receiver.py

# Acessar
http://localhost:5000/webhook/fiscal
```

### 2. `sync_nfes.py`

**Sincronização automática de NFes via API**

- Busca NFes periodicamente
- Sincroniza com seu banco de dados
- Executa em loop contínuo
- Logging completo

**Como usar:**

```bash
# Instalar dependências
pip install requests sqlalchemy

# Configurar token
# Edite FISCAL_API_TOKEN no arquivo

# Executar
python sync_nfes.py
```

### 3. `slack_notifier.py`

**Envia notificações para Slack**

- Recebe webhooks
- Formata mensagens bonitas
- Envia para canal do Slack
- Cores diferentes por tipo de evento

**Como usar:**

```bash
# Instalar dependências
pip install flask requests

# Configurar Slack Webhook URL
# 1. Acesse https://api.slack.com/messaging/webhooks
# 2. Crie um Incoming Webhook
# 3. Configure SLACK_WEBHOOK_URL no arquivo

# Executar
python slack_notifier.py
```

---

## 🔧 Configuração Geral

### 1. Obter Token de API

```python
import requests

response = requests.post(
    'http://localhost:8000/api/auth/login/',
    json={
        'username': 'seu-usuario',
        'password': 'sua-senha'
    }
)

token = response.json()['token']
print(f"Token: {token}")
```

### 2. Configurar Webhook

```python
import requests

response = requests.post(
    'http://localhost:8000/api/webhooks/',
    headers={
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    },
    json={
        'nome': 'Meu Webhook',
        'url': 'http://seu-servidor:5000/webhook/fiscal',
        'eventos': 'nfe_importada,cte_importado',
        'ativo': True,
        'secret_key': 'chave-secreta'
    }
)

webhook = response.json()
print(f"Webhook criado: ID {webhook['id']}")
```

---

## 🚀 Executando em Produção

### Com Systemd (Linux)

Crie `/etc/systemd/system/fiscal-sync.service`:

```ini
[Unit]
Description=Fiscal NFe Sync Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/exemplos
ExecStart=/usr/bin/python sync_nfes.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Ative:

```bash
sudo systemctl enable fiscal-sync
sudo systemctl start fiscal-sync
sudo systemctl status fiscal-sync
```

### Com Docker

Crie `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY *.py .

CMD ["python", "sync_nfes.py"]
```

Execute:

```bash
docker build -t fiscal-sync .
docker run -d --name fiscal-sync fiscal-sync
```

### Com Supervisor

Crie `/etc/supervisor/conf.d/fiscal-sync.conf`:

```ini
[program:fiscal-sync]
command=/usr/bin/python /path/to/exemplos/sync_nfes.py
directory=/path/to/exemplos
autostart=true
autorestart=true
user=www-data
stdout_logfile=/var/log/fiscal-sync.log
stderr_logfile=/var/log/fiscal-sync-error.log
```

Recarregue:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start fiscal-sync
```

---

## 🔒 Segurança

### Validação de Assinatura

Sempre valide assinaturas HMAC em webhooks:

```python
import hmac
import hashlib

def validar_assinatura(payload, signature, secret_key):
    expected = hmac.new(
        secret_key.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected)
```

### Uso de HTTPS

Em produção, sempre use HTTPS:

```python
# Configure seu webhook com URL HTTPS
webhook_url = 'https://seu-dominio.com/webhook/fiscal'
```

### Variáveis de Ambiente

Use variáveis de ambiente para credenciais:

```python
import os

FISCAL_API_TOKEN = os.environ.get('FISCAL_API_TOKEN')
SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')
SECRET_KEY = os.environ.get('WEBHOOK_SECRET_KEY')
```

---

## 📊 Monitoramento

### Logs

Todos os exemplos geram logs:

```bash
# webhook_receiver.py
tail -f webhook_receiver.log

# sync_nfes.py
tail -f sync_nfes.log
```

### Health Checks

Todos os exemplos possuem endpoint de health check:

```bash
curl http://localhost:5000/health
```

### Métricas

Monitore métricas importantes:

- Taxa de sucesso de webhooks
- Tempo de resposta
- Número de eventos processados
- Erros

---

## 🆘 Troubleshooting

### Webhook não recebe eventos

1. Verifique se webhook está ativo
2. Teste com `/api/webhooks/{id}/testar/`
3. Verifique logs do webhook
4. Confirme que URL está acessível

### Erro de autenticação

1. Verifique se token está correto
2. Token não expirou?
3. Usuário tem permissões?

### Erro de validação de assinatura

1. Confirme que SECRET_KEY é o mesmo em ambos os lados
2. Payload não foi modificado?
3. Encoding está correto (UTF-8)?

---

## 📞 Suporte

- **Documentação**: `../INTEGRACOES.md`
- **API Reference**: http://localhost:8000/api/
- **Issues**: GitHub Issues

---

**💡 Dica:** Use estes exemplos como base para criar suas próprias integrações!
