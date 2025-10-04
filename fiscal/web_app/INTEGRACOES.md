# 🔗 Sistema de Integrações e Automações

Documentação completa do sistema de integrações, webhooks e automações para o Sistema Fiscal.

---

## 📋 Índice

1. [Webhooks](#webhooks)
2. [API de Integrações](#api-de-integrações)
3. [Tarefas Agendadas](#tarefas-agendadas)
4. [Eventos Disponíveis](#eventos-disponíveis)
5. [Exemplos de Uso](#exemplos-de-uso)
6. [Segurança](#segurança)

---

## 🎯 Webhooks

Webhooks permitem que seu sistema receba notificações em tempo real quando eventos importantes ocorrem.

### Configuração de Webhook

#### Via API

```bash
POST /api/webhooks/
Authorization: Token SEU_TOKEN

{
  "nome": "Meu Webhook de Produção",
  "url": "https://meu-sistema.com.br/webhook/fiscal",
  "eventos": "nfe_importada,cte_importado,consulta_concluida",
  "ativo": true,
  "secret_key": "chave-secreta-para-validacao",
  "timeout": 30,
  "retry_count": 3,
  "headers_customizados": "{\"X-Custom-Header\": \"valor\"}"
}
```

#### Campos

- **nome**: Nome identificador do webhook
- **url**: URL que receberá as notificações POST
- **eventos**: Eventos separados por vírgula
- **ativo**: Se o webhook está ativo (true/false)
- **secret_key**: Chave secreta para validação HMAC (opcional)
- **timeout**: Tempo máximo de espera em segundos (padrão: 30)
- **retry_count**: Número de tentativas em caso de falha (padrão: 3)
- **headers_customizados**: Headers HTTP customizados em formato JSON

### Eventos Disponíveis

| Evento | Descrição | Dados Enviados |
|--------|-----------|----------------|
| `nfe_importada` | Disparado quando uma NFe é importada | `chave_acesso`, `numero_nf`, `emit_nome`, `valor_total` |
| `cte_importado` | Disparado quando um CTe é importado | `chave_acesso`, `numero_ct`, `emit_nome`, `valor_total` |
| `consulta_concluida` | Disparado quando consulta SEFAZ é concluída | `certificado`, `cnpj`, `total_encontrados`, `data_inicio`, `data_fim` |
| `documento_atualizado` | Disparado quando um documento é atualizado | `chave_acesso`, `tipo`, `campos_alterados` |
| `erro_importacao` | Disparado quando ocorre erro na importação | `arquivo`, `erro`, `timestamp` |

### Payload do Webhook

Quando um evento ocorre, seu webhook recebe um POST com o seguinte formato:

```json
{
  "evento": "nfe_importada",
  "timestamp": "2024-10-04T10:30:00Z",
  "dados": {
    "chave_acesso": "35210812345678901234567890123456789012345678",
    "numero_nf": "12345",
    "serie": "1",
    "emit_cnpj": "12345678901234",
    "emit_nome": "Empresa Exemplo LTDA",
    "dest_nome": "Cliente Exemplo",
    "valor_total": "1500.00",
    "data_emissao": "2024-10-03",
    "usuario": "admin"
  }
}
```

### Validação de Segurança

Se você configurou um `secret_key`, o webhook incluirá um header `X-Webhook-Signature` com a assinatura HMAC-SHA256 do payload:

```python
import hmac
import hashlib
import json

def validar_webhook(payload_json, signature, secret_key):
    """Valida assinatura do webhook"""
    expected = hmac.new(
        secret_key.encode(),
        payload_json.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected)

# Exemplo de uso
payload = request.body.decode('utf-8')
signature = request.headers.get('X-Webhook-Signature')
secret = 'sua-chave-secreta'

if validar_webhook(payload, signature, secret):
    print("✓ Webhook válido")
else:
    print("✗ Webhook inválido")
```

---

## 🔌 API de Integrações

### Endpoints de Webhook

#### Listar Webhooks

```bash
GET /api/webhooks/
Authorization: Token SEU_TOKEN
```

Resposta:
```json
[
  {
    "id": 1,
    "nome": "Webhook Produção",
    "url": "https://meu-sistema.com.br/webhook",
    "eventos": "nfe_importada,cte_importado",
    "eventos_list": ["nfe_importada", "cte_importado"],
    "ativo": true,
    "timeout": 30,
    "retry_count": 3,
    "data_criacao": "2024-10-01T10:00:00Z",
    "ultima_execucao": "2024-10-04T09:30:00Z",
    "total_execucoes": 150,
    "total_erros": 2,
    "usuario_nome": "admin"
  }
]
```

#### Criar Webhook

```bash
POST /api/webhooks/
Authorization: Token SEU_TOKEN
Content-Type: application/json

{
  "nome": "Novo Webhook",
  "url": "https://exemplo.com/webhook",
  "eventos": "nfe_importada",
  "ativo": true
}
```

#### Atualizar Webhook

```bash
PUT /api/webhooks/{id}/
Authorization: Token SEU_TOKEN
Content-Type: application/json

{
  "ativo": false
}
```

#### Deletar Webhook

```bash
DELETE /api/webhooks/{id}/
Authorization: Token SEU_TOKEN
```

#### Testar Webhook

Envia um webhook de teste para validar a configuração:

```bash
POST /api/webhooks/{id}/testar/
Authorization: Token SEU_TOKEN
```

Resposta:
```json
{
  "status": "success",
  "mensagem": "Webhook enviado com sucesso"
}
```

#### Ver Logs do Webhook

```bash
GET /api/webhooks/{id}/logs/
Authorization: Token SEU_TOKEN
```

Resposta:
```json
[
  {
    "id": 1,
    "webhook_nome": "Webhook Produção",
    "evento": "nfe_importada",
    "data_execucao": "2024-10-04T09:30:00Z",
    "sucesso": true,
    "status_code": 200,
    "payload": "{...}",
    "response": "OK"
  }
]
```

#### Estatísticas de Webhooks

```bash
GET /api/webhooks/estatisticas/
Authorization: Token SEU_TOKEN
```

Resposta:
```json
{
  "total_webhooks": 5,
  "webhooks_ativos": 4,
  "execucoes_24h": 123,
  "taxa_sucesso": 98.5,
  "total_logs": 150,
  "logs_sucesso": 148
}
```

### Disparar Eventos Manualmente

```bash
POST /api/integracoes/disparar/
Authorization: Token SEU_TOKEN
Content-Type: application/json

{
  "evento": "nfe_importada",
  "dados": {
    "chave_acesso": "35210812345678901234567890123456789012345678",
    "numero_nf": "12345",
    "valor_total": "1500.00"
  }
}
```

### Listar Eventos Disponíveis

```bash
GET /api/integracoes/eventos/
Authorization: Token SEU_TOKEN
```

Resposta:
```json
{
  "eventos": [
    {
      "id": "nfe_importada",
      "nome": "NFe Importada",
      "descricao": "Disparado quando nfe importada"
    },
    {
      "id": "cte_importado",
      "nome": "CTe Importado",
      "descricao": "Disparado quando cte importado"
    }
  ],
  "total": 5
}
```

---

## ⏰ Tarefas Agendadas

O sistema possui um comando Django para executar tarefas automáticas.

### Executar Todas as Tarefas

```bash
python manage.py run_scheduled_tasks
```

### Executar Tarefa Específica

```bash
# Consultas automáticas SEFAZ
python manage.py run_scheduled_tasks --task=consultas_sefaz

# Limpeza de logs antigos
python manage.py run_scheduled_tasks --task=limpeza_logs

# Envio de relatórios diários
python manage.py run_scheduled_tasks --task=enviar_relatorios
```

### Agendar com Cron

Adicione ao crontab para execução automática:

```bash
# Executa todas as tarefas a cada hora
0 * * * * cd /path/to/project && python manage.py run_scheduled_tasks

# Consultas SEFAZ a cada 30 minutos
*/30 * * * * cd /path/to/project && python manage.py run_scheduled_tasks --task=consultas_sefaz

# Limpeza de logs todo dia às 2h
0 2 * * * cd /path/to/project && python manage.py run_scheduled_tasks --task=limpeza_logs

# Relatórios diários às 8h
0 8 * * * cd /path/to/project && python manage.py run_scheduled_tasks --task=enviar_relatorios
```

### Agendar com Cloud Scheduler (Google Cloud)

```bash
# Criar job no Cloud Scheduler
gcloud scheduler jobs create http consultas-sefaz \
  --schedule="0 * * * *" \
  --uri="https://seu-app.appspot.com/api/trigger-tasks/" \
  --http-method=POST \
  --headers="Authorization=Bearer TOKEN"
```

---

## 📝 Exemplos de Uso

### Exemplo 1: Integração com Sistema ERP

```python
# webhook_receiver.py
from flask import Flask, request, jsonify
import hmac
import hashlib

app = Flask(__name__)
SECRET_KEY = 'sua-chave-secreta'

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
        return jsonify({'error': 'Invalid signature'}), 401
    
    # Processa evento
    data = request.json
    evento = data['evento']
    
    if evento == 'nfe_importada':
        processar_nfe(data['dados'])
    elif evento == 'cte_importado':
        processar_cte(data['dados'])
    
    return jsonify({'status': 'ok'}), 200

def processar_nfe(dados):
    """Processa NFe no ERP"""
    print(f"Nova NFe: {dados['numero_nf']}")
    # Importa para o ERP
    # erp.importar_nfe(dados)

if __name__ == '__main__':
    app.run(port=5000)
```

### Exemplo 2: Notificação via Slack

```python
import requests

def notificar_slack(evento, dados):
    """Envia notificação para Slack"""
    webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    
    if evento == 'nfe_importada':
        mensagem = f"✅ Nova NFe importada!\n" \
                  f"Número: {dados['numero_nf']}\n" \
                  f"Emitente: {dados['emit_nome']}\n" \
                  f"Valor: R$ {dados['valor_total']}"
    elif evento == 'erro_importacao':
        mensagem = f"❌ Erro na importação!\n" \
                  f"Arquivo: {dados['arquivo']}\n" \
                  f"Erro: {dados['erro']}"
    
    payload = {
        "text": mensagem,
        "username": "Fiscal Bot",
        "icon_emoji": ":receipt:"
    }
    
    requests.post(webhook_url, json=payload)
```

### Exemplo 3: Sincronização com Google Sheets

```python
from googleapiclient.discovery import build
from google.oauth2 import service_account

def adicionar_nfe_planilha(dados):
    """Adiciona NFe em planilha Google Sheets"""
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = 'credentials.json'
    SPREADSHEET_ID = 'your-spreadsheet-id'
    
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    
    service = build('sheets', 'v4', credentials=credentials)
    
    # Prepara dados
    values = [[
        dados['numero_nf'],
        dados['data_emissao'],
        dados['emit_nome'],
        dados['dest_nome'],
        dados['valor_total']
    ]]
    
    body = {'values': values}
    
    # Adiciona linha
    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range='NFes!A:E',
        valueInputOption='USER_ENTERED',
        body=body
    ).execute()
```

---

## 🔒 Segurança

### Boas Práticas

1. **Use sempre HTTPS** para URLs de webhook
2. **Configure secret_key** para validar assinaturas
3. **Valide assinaturas** em todos os webhooks recebidos
4. **Use tokens de API** com permissões mínimas
5. **Configure timeout** adequado (máx 30 segundos)
6. **Monitore logs** regularmente
7. **Use IP whitelist** quando possível

### Validação de IP (Opcional)

```python
ALLOWED_IPS = ['34.123.45.67', '35.234.56.78']

@app.route('/webhook/fiscal', methods=['POST'])
def webhook_fiscal():
    client_ip = request.remote_addr
    
    if client_ip not in ALLOWED_IPS:
        return jsonify({'error': 'IP not allowed'}), 403
    
    # Processa webhook...
```

### Rate Limiting

Configure rate limiting para evitar abuso:

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    default_limits=["100 per hour"]
)

@app.route('/webhook/fiscal', methods=['POST'])
@limiter.limit("60 per minute")
def webhook_fiscal():
    # Processa webhook...
```

---

## 📞 Suporte

Para dúvidas ou problemas:

1. Verifique os logs do webhook em `/api/webhooks/{id}/logs/`
2. Teste o webhook com `/api/webhooks/{id}/testar/`
3. Consulte as estatísticas em `/api/webhooks/estatisticas/`
4. Revise a documentação da API

---

**🔗 Sistema completo de integrações e automações!**
