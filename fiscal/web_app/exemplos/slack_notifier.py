"""
Exemplo: Enviar notificações para Slack quando NFe/CTe são importados

Este script recebe webhooks e envia notificações para o Slack.

Instalação:
    pip install flask requests

Uso:
    1. Configure SLACK_WEBHOOK_URL com sua URL do Slack
    2. Execute: python slack_notifier.py
    3. Configure webhook no Sistema Fiscal apontando para http://seu-servidor:5000/webhook/fiscal
"""

from flask import Flask, request, jsonify
import requests
import hmac
import hashlib

app = Flask(__name__)

# CONFIGURAÇÃO: Obtenha em https://api.slack.com/messaging/webhooks
SLACK_WEBHOOK_URL = 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
SECRET_KEY = 'sua-chave-secreta'


def validar_assinatura(payload, signature):
    """Valida assinatura HMAC do webhook"""
    if not SECRET_KEY or SECRET_KEY == 'sua-chave-secreta':
        return True  # Skip validation se não configurado
    
    expected = hmac.new(
        SECRET_KEY.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected)


def enviar_slack(mensagem, cor='good', titulo='Sistema Fiscal'):
    """
    Envia mensagem para Slack
    
    Args:
        mensagem: Texto da mensagem
        cor: Cor da barra lateral (good, warning, danger)
        titulo: Título da mensagem
    """
    if SLACK_WEBHOOK_URL == 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL':
        print(f"⚠️ SLACK_WEBHOOK_URL não configurado. Mensagem: {mensagem}")
        return
    
    payload = {
        'username': 'Fiscal Bot',
        'icon_emoji': ':receipt:',
        'attachments': [
            {
                'color': cor,
                'title': titulo,
                'text': mensagem,
                'footer': 'Sistema Fiscal',
                'ts': int(request.json['timestamp']) if request.json else 0
            }
        ]
    }
    
    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print(f"✓ Mensagem enviada para Slack")
    except Exception as e:
        print(f"❌ Erro ao enviar para Slack: {str(e)}")


@app.route('/webhook/fiscal', methods=['POST'])
def webhook_fiscal():
    """Recebe webhooks e envia para Slack"""
    
    # Valida assinatura
    signature = request.headers.get('X-Webhook-Signature')
    payload = request.data.decode('utf-8')
    
    if signature and not validar_assinatura(payload, signature):
        return jsonify({'error': 'Invalid signature'}), 401
    
    # Processa evento
    data = request.json
    evento = data.get('evento')
    dados = data.get('dados', {})
    
    # Envia notificação baseada no evento
    if evento == 'nfe_importada':
        mensagem = (
            f"*Nova NFe Importada!* :white_check_mark:\n\n"
            f"*Número:* {dados.get('numero_nf')} (Série {dados.get('serie')})\n"
            f"*Emitente:* {dados.get('emit_nome')}\n"
            f"*Destinatário:* {dados.get('dest_nome')}\n"
            f"*Valor Total:* R$ {float(dados.get('valor_total', 0)):,.2f}\n"
            f"*Data Emissão:* {dados.get('data_emissao', 'N/A')}\n"
            f"*Chave:* `{dados.get('chave_acesso')}`"
        )
        enviar_slack(mensagem, cor='good', titulo='📄 NFe Importada')
    
    elif evento == 'cte_importado':
        mensagem = (
            f"*Novo CTe Importado!* :truck:\n\n"
            f"*Número:* {dados.get('numero_ct')} (Série {dados.get('serie')})\n"
            f"*Emitente:* {dados.get('emit_nome')}\n"
            f"*Origem:* {dados.get('municipio_inicio')}/{dados.get('uf_inicio')}\n"
            f"*Destino:* {dados.get('municipio_fim')}/{dados.get('uf_fim')}\n"
            f"*Valor Total:* R$ {float(dados.get('valor_total', 0)):,.2f}\n"
            f"*Chave:* `{dados.get('chave_acesso')}`"
        )
        enviar_slack(mensagem, cor='good', titulo='🚚 CTe Importado')
    
    elif evento == 'consulta_concluida':
        mensagem = (
            f"*Consulta SEFAZ Concluída!* :bar_chart:\n\n"
            f"*Certificado:* {dados.get('certificado_nome')}\n"
            f"*CNPJ:* {dados.get('cnpj')}\n"
            f"*Período:* {dados.get('data_inicio')} até {dados.get('data_fim')}\n"
            f"*Documentos Encontrados:* {dados.get('total_encontrados')}\n"
            f"*Importados:* {dados.get('total_importados')}\n"
            f"*Erros:* {dados.get('total_erros')}"
        )
        enviar_slack(mensagem, cor='good', titulo='📊 Consulta Concluída')
    
    elif evento == 'erro_importacao':
        mensagem = (
            f"*Erro na Importação!* :x:\n\n"
            f"*Tipo:* {dados.get('tipo_documento')}\n"
            f"*Arquivo:* {dados.get('arquivo_nome')}\n"
            f"*Erro:* {dados.get('mensagem')}\n"
            f"*Chave:* `{dados.get('chave_acesso', 'N/A')}`"
        )
        enviar_slack(mensagem, cor='danger', titulo='❌ Erro de Importação')
    
    return jsonify({'status': 'ok'}), 200


@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'ok',
        'service': 'Slack Notifier',
        'slack_configured': SLACK_WEBHOOK_URL != 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
    })


if __name__ == '__main__':
    print("🚀 Iniciando Slack Notifier...")
    print(f"📡 Endpoint: http://localhost:5000/webhook/fiscal")
    print(f"💬 Slack: {'Configurado' if SLACK_WEBHOOK_URL != 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL' else 'NÃO CONFIGURADO'}")
    print(f"🔐 Secret Key: {'Configurado' if SECRET_KEY != 'sua-chave-secreta' else 'NÃO CONFIGURADO'}")
    print("\n⚠️  Configure SLACK_WEBHOOK_URL em: https://api.slack.com/messaging/webhooks")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
