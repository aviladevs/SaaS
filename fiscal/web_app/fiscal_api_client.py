"""
Cliente Python para integração com a API Fiscal
Facilita a comunicação entre serviços internos
"""
import requests
import json
from typing import Dict, List, Optional
from datetime import datetime, date


class FiscalAPIClient:
    """
    Cliente para integração com API Fiscal
    
    Uso:
        client = FiscalAPIClient('http://localhost:8000', 'seu-token')
        nfes = client.listar_nfes(limit=10)
        webhook = client.criar_webhook('Meu Webhook', 'https://exemplo.com/webhook')
    """
    
    def __init__(self, base_url: str, token: str, timeout: int = 30):
        """
        Inicializa cliente
        
        Args:
            base_url: URL base da API (ex: http://localhost:8000)
            token: Token de autenticação
            timeout: Timeout em segundos
        """
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Token {token}',
            'Content-Type': 'application/json'
        })
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Faz requisição HTTP"""
        url = f"{self.base_url}/api/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(
                method,
                url,
                timeout=kwargs.pop('timeout', self.timeout),
                **kwargs
            )
            response.raise_for_status()
            
            if response.content:
                return response.json()
            return {}
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erro na requisição: {str(e)}")
    
    # NFe Endpoints
    
    def listar_nfes(self, search: str = '', cnpj: str = '', 
                    data_inicio: Optional[date] = None,
                    data_fim: Optional[date] = None,
                    page: int = 1, limit: int = 20) -> Dict:
        """Lista NFes com filtros"""
        params = {'page': page}
        
        if search:
            params['search'] = search
        if cnpj:
            params['cnpj'] = cnpj
        if data_inicio:
            params['data_inicio'] = data_inicio.isoformat()
        if data_fim:
            params['data_fim'] = data_fim.isoformat()
        
        return self._request('GET', 'nfe/', params=params)
    
    def buscar_nfe(self, nfe_id: int) -> Dict:
        """Busca NFe por ID"""
        return self._request('GET', f'nfe/{nfe_id}/')
    
    def totais_nfe(self) -> Dict:
        """Retorna totalizadores de NFes"""
        return self._request('GET', 'nfe/totais/')
    
    def nfes_por_emitente(self) -> List[Dict]:
        """Agrupa NFes por emitente"""
        return self._request('GET', 'nfe/por_emitente/')
    
    # CTe Endpoints
    
    def listar_ctes(self, search: str = '', page: int = 1) -> Dict:
        """Lista CTes"""
        params = {'page': page}
        if search:
            params['search'] = search
        
        return self._request('GET', 'cte/', params=params)
    
    def buscar_cte(self, cte_id: int) -> Dict:
        """Busca CTe por ID"""
        return self._request('GET', f'cte/{cte_id}/')
    
    def totais_cte(self) -> Dict:
        """Retorna totalizadores de CTes"""
        return self._request('GET', 'cte/totais/')
    
    def ctes_por_rota(self) -> List[Dict]:
        """Agrupa CTes por rota"""
        return self._request('GET', 'cte/rotas/')
    
    # Dashboard e Estatísticas
    
    def dashboard(self) -> Dict:
        """Retorna dados do dashboard"""
        return self._request('GET', 'dashboard/')
    
    def estatisticas(self) -> Dict:
        """Retorna estatísticas completas"""
        return self._request('GET', 'statistics/')
    
    def buscar(self, termo: str) -> Dict:
        """Busca unificada em NFes e CTes"""
        return self._request('GET', 'search/', params={'q': termo})
    
    # Webhooks
    
    def listar_webhooks(self) -> List[Dict]:
        """Lista todos os webhooks do usuário"""
        return self._request('GET', 'webhooks/')
    
    def criar_webhook(self, nome: str, url: str, eventos: str,
                     ativo: bool = True, secret_key: str = '',
                     timeout: int = 30, retry_count: int = 3) -> Dict:
        """
        Cria novo webhook
        
        Args:
            nome: Nome do webhook
            url: URL que receberá notificações
            eventos: Eventos separados por vírgula (ex: "nfe_importada,cte_importado")
            ativo: Se webhook está ativo
            secret_key: Chave secreta para validação
            timeout: Timeout em segundos
            retry_count: Número de tentativas
        """
        data = {
            'nome': nome,
            'url': url,
            'eventos': eventos,
            'ativo': ativo,
            'timeout': timeout,
            'retry_count': retry_count
        }
        
        if secret_key:
            data['secret_key'] = secret_key
        
        return self._request('POST', 'webhooks/', json=data)
    
    def atualizar_webhook(self, webhook_id: int, **kwargs) -> Dict:
        """Atualiza webhook"""
        return self._request('PUT', f'webhooks/{webhook_id}/', json=kwargs)
    
    def deletar_webhook(self, webhook_id: int) -> None:
        """Deleta webhook"""
        self._request('DELETE', f'webhooks/{webhook_id}/')
    
    def testar_webhook(self, webhook_id: int) -> Dict:
        """Testa envio de webhook"""
        return self._request('POST', f'webhooks/{webhook_id}/testar/')
    
    def logs_webhook(self, webhook_id: int) -> List[Dict]:
        """Retorna logs do webhook"""
        return self._request('GET', f'webhooks/{webhook_id}/logs/')
    
    def estatisticas_webhooks(self) -> Dict:
        """Retorna estatísticas de webhooks"""
        return self._request('GET', 'webhooks/estatisticas/')
    
    # Integrações
    
    def eventos_disponiveis(self) -> Dict:
        """Lista eventos disponíveis para webhooks"""
        return self._request('GET', 'integracoes/eventos/')
    
    def disparar_evento(self, evento: str, dados: Dict) -> Dict:
        """
        Dispara evento manualmente
        
        Args:
            evento: Nome do evento
            dados: Dados do evento
        """
        return self._request('POST', 'integracoes/disparar/', json={
            'evento': evento,
            'dados': dados
        })
    
    # Logs
    
    def listar_logs(self, tipo: str = '', status: str = '', page: int = 1) -> Dict:
        """Lista logs de importação"""
        params = {'page': page}
        if tipo:
            params['tipo'] = tipo
        if status:
            params['status'] = status
        
        return self._request('GET', 'logs/', params=params)


# Exemplo de uso
if __name__ == '__main__':
    # Configuração
    API_URL = 'http://localhost:8000'
    API_TOKEN = 'seu-token-aqui'
    
    # Cria cliente
    client = FiscalAPIClient(API_URL, API_TOKEN)
    
    # Lista NFes
    print("📄 Listando NFes...")
    nfes = client.listar_nfes(limit=5)
    print(f"Total: {nfes.get('count', 0)} NFes")
    
    # Dashboard
    print("\n📊 Dashboard...")
    dashboard = client.dashboard()
    print(f"NFes: {dashboard['nfe_total']}")
    print(f"CTes: {dashboard['cte_total']}")
    
    # Cria webhook
    print("\n🔗 Criando webhook...")
    webhook = client.criar_webhook(
        nome='Webhook de Teste',
        url='https://webhook.site/seu-uuid',
        eventos='nfe_importada,cte_importado',
        ativo=True
    )
    print(f"Webhook criado: ID {webhook['id']}")
    
    # Testa webhook
    print("\n✅ Testando webhook...")
    resultado = client.testar_webhook(webhook['id'])
    print(f"Resultado: {resultado['status']}")
    
    # Lista eventos disponíveis
    print("\n📋 Eventos disponíveis...")
    eventos = client.eventos_disponiveis()
    for evento in eventos['eventos']:
        print(f"  - {evento['id']}: {evento['nome']}")
