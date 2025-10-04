"""
Exemplo: Receber webhooks do Sistema Fiscal em um servidor Flask

Este script cria um servidor Flask que recebe notificações do Sistema Fiscal
via webhooks e processa os eventos.

Instalação:
    pip install flask requests

Uso:
    python webhook_receiver.py
    
    Depois configure seu webhook para apontar para:
    http://seu-servidor:5000/webhook/fiscal
"""

from flask import Flask, request, jsonify
import hmac
import hashlib
import json
from datetime import datetime

app = Flask(__name__)

# CONFIGURAÇÃO: Substitua pela sua chave secreta configurada no webhook
SECRET_KEY = 'sua-chave-secreta'

# Armazena eventos recebidos (em produção, use banco de dados)
eventos_recebidos = []


def validar_assinatura(payload, signature):
    """
    Valida assinatura HMAC do webhook
    
    Args:
        payload: Corpo da requisição (string)
        signature: Assinatura recebida no header X-Webhook-Signature
        
    Returns:
        bool: True se válido
    """
    expected = hmac.new(
        SECRET_KEY.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected)


@app.route('/webhook/fiscal', methods=['POST'])
def webhook_fiscal():
    """
    Endpoint que recebe webhooks do Sistema Fiscal
    """
    
    # Valida assinatura se SECRET_KEY estiver configurado
    if SECRET_KEY and SECRET_KEY != 'sua-chave-secreta':
        signature = request.headers.get('X-Webhook-Signature')
        payload = request.data.decode('utf-8')
        
        if not signature or not validar_assinatura(payload, signature):
            return jsonify({'error': 'Invalid signature'}), 401
    
    # Parseia dados
    data = request.json
    evento = data.get('evento')
    timestamp = data.get('timestamp')
    dados = data.get('dados', {})
    
    print(f"\n{'='*60}")
    print(f"📬 Webhook recebido: {evento}")
    print(f"⏰ Timestamp: {timestamp}")
    print(f"{'='*60}\n")
    
    # Processa evento
    if evento == 'nfe_importada':
        processar_nfe_importada(dados)
    
    elif evento == 'cte_importado':
        processar_cte_importado(dados)
    
    elif evento == 'consulta_concluida':
        processar_consulta_concluida(dados)
    
    elif evento == 'erro_importacao':
        processar_erro_importacao(dados)
    
    else:
        print(f"⚠️ Evento desconhecido: {evento}")
    
    # Armazena evento
    eventos_recebidos.append({
        'evento': evento,
        'timestamp': timestamp,
        'dados': dados,
        'recebido_em': datetime.now().isoformat()
    })
    
    # Retorna sucesso
    return jsonify({'status': 'ok', 'evento': evento}), 200


def processar_nfe_importada(dados):
    """Processa evento de NFe importada"""
    print("📄 NFe Importada:")
    print(f"  Número: {dados.get('numero_nf')}")
    print(f"  Série: {dados.get('serie')}")
    print(f"  Emitente: {dados.get('emit_nome')}")
    print(f"  Destinatário: {dados.get('dest_nome')}")
    print(f"  Valor: R$ {dados.get('valor_total')}")
    print(f"  Chave: {dados.get('chave_acesso')}")
    
    # Aqui você pode:
    # - Enviar para seu ERP
    # - Salvar no banco de dados
    # - Enviar notificação por email/Slack
    # - Atualizar dashboard
    # etc.


def processar_cte_importado(dados):
    """Processa evento de CTe importado"""
    print("🚚 CTe Importado:")
    print(f"  Número: {dados.get('numero_ct')}")
    print(f"  Emitente: {dados.get('emit_nome')}")
    print(f"  Origem: {dados.get('municipio_inicio')}/{dados.get('uf_inicio')}")
    print(f"  Destino: {dados.get('municipio_fim')}/{dados.get('uf_fim')}")
    print(f"  Valor: R$ {dados.get('valor_total')}")


def processar_consulta_concluida(dados):
    """Processa evento de consulta SEFAZ concluída"""
    print("📊 Consulta SEFAZ Concluída:")
    print(f"  Certificado: {dados.get('certificado_nome')}")
    print(f"  CNPJ: {dados.get('cnpj')}")
    print(f"  Documentos encontrados: {dados.get('total_encontrados')}")
    print(f"  Importados: {dados.get('total_importados')}")


def processar_erro_importacao(dados):
    """Processa evento de erro na importação"""
    print("❌ Erro na Importação:")
    print(f"  Tipo: {dados.get('tipo_documento')}")
    print(f"  Arquivo: {dados.get('arquivo_nome')}")
    print(f"  Erro: {dados.get('mensagem')}")


@app.route('/eventos', methods=['GET'])
def listar_eventos():
    """Lista todos os eventos recebidos"""
    return jsonify({
        'total': len(eventos_recebidos),
        'eventos': eventos_recebidos
    })


@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'ok',
        'service': 'Webhook Receiver',
        'eventos_recebidos': len(eventos_recebidos)
    })


if __name__ == '__main__':
    print("🚀 Iniciando servidor de webhooks...")
    print(f"📡 Endpoint: http://localhost:5000/webhook/fiscal")
    print(f"🔐 Secret Key: {'Configurado' if SECRET_KEY != 'sua-chave-secreta' else 'NÃO CONFIGURADO'}")
    print("\n⚠️  Lembre-se de:")
    print("  1. Configurar SECRET_KEY com a mesma chave do webhook")
    print("  2. Expor esta porta para a internet (ou usar ngrok para testes)")
    print("  3. Configurar o webhook no Sistema Fiscal apontando para esta URL")
    print("\n" + "="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
