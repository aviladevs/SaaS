"""
Exemplo: Sincronizar NFes do Sistema Fiscal para outro banco de dados

Este script busca NFes via API e sincroniza com outro banco de dados.

Instalação:
    pip install requests sqlalchemy

Uso:
    python sync_nfes.py
"""

import sys
import os

# Adiciona o diretório pai ao path para importar fiscal_api_client
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fiscal_api_client import FiscalAPIClient
from datetime import datetime, timedelta
import time
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# CONFIGURAÇÃO
FISCAL_API_URL = 'http://localhost:8000'
FISCAL_API_TOKEN = 'seu-token-aqui'

# Intervalo de sincronização (minutos)
SYNC_INTERVAL = 5


class NFeSyncService:
    """Serviço de sincronização de NFes"""
    
    def __init__(self, api_url, api_token):
        self.client = FiscalAPIClient(api_url, api_token)
        self.ultima_sync = None
        self.total_sincronizadas = 0
    
    def sincronizar(self):
        """
        Sincroniza NFes recentes
        """
        logger.info("🔄 Iniciando sincronização...")
        
        try:
            # Busca NFes
            if self.ultima_sync:
                # Busca apenas NFes após última sync
                data_inicio = self.ultima_sync.date()
                nfes = self.client.listar_nfes(
                    data_inicio=data_inicio,
                    limit=100
                )
            else:
                # Primeira execução: busca últimos 7 dias
                data_inicio = (datetime.now() - timedelta(days=7)).date()
                nfes = self.client.listar_nfes(
                    data_inicio=data_inicio,
                    limit=100
                )
            
            total = nfes.get('count', 0)
            logger.info(f"📄 {total} NFes encontradas")
            
            # Processa cada NFe
            for nfe in nfes.get('results', []):
                self.processar_nfe(nfe)
                time.sleep(0.1)  # Evita sobrecarga
            
            self.ultima_sync = datetime.now()
            logger.info(f"✓ Sincronização concluída")
            
        except Exception as e:
            logger.error(f"❌ Erro na sincronização: {str(e)}")
    
    def processar_nfe(self, nfe):
        """
        Processa uma NFe
        
        Args:
            nfe: Dados da NFe
        """
        chave = nfe.get('chave_acesso')
        numero = nfe.get('numero_nf')
        
        logger.info(f"  Processando NFe {numero}...")
        
        # Aqui você implementaria a lógica de:
        # 1. Verificar se NFe já existe no seu banco
        # 2. Inserir/atualizar no seu banco
        # 3. Buscar detalhes completos se necessário
        
        # Exemplo: Buscar detalhes completos
        # nfe_id = nfe['id']
        # detalhes = self.client.buscar_nfe(nfe_id)
        
        # Exemplo: Salvar no banco
        # db.save_nfe(nfe)
        
        self.total_sincronizadas += 1
        
        logger.info(f"  ✓ NFe {numero} processada")
    
    def executar_loop(self):
        """
        Executa sincronização em loop
        """
        logger.info(f"🚀 Iniciando serviço de sincronização...")
        logger.info(f"⏰ Intervalo: {SYNC_INTERVAL} minutos")
        logger.info(f"🔗 API: {FISCAL_API_URL}")
        logger.info("")
        
        while True:
            try:
                self.sincronizar()
                
                logger.info(f"💤 Aguardando {SYNC_INTERVAL} minutos...")
                logger.info(f"📊 Total sincronizado: {self.total_sincronizadas} NFes\n")
                
                time.sleep(SYNC_INTERVAL * 60)
                
            except KeyboardInterrupt:
                logger.info("\n⏹️  Serviço interrompido pelo usuário")
                break
            except Exception as e:
                logger.error(f"❌ Erro no loop: {str(e)}")
                logger.info("⏳ Aguardando 1 minuto antes de tentar novamente...")
                time.sleep(60)


def main():
    """Função principal"""
    
    # Valida configuração
    if FISCAL_API_TOKEN == 'seu-token-aqui':
        logger.error("❌ Configure FISCAL_API_TOKEN antes de executar")
        return
    
    # Cria serviço
    service = NFeSyncService(FISCAL_API_URL, FISCAL_API_TOKEN)
    
    # Executa
    try:
        service.executar_loop()
    except KeyboardInterrupt:
        logger.info("\n👋 Encerrando serviço...")


if __name__ == '__main__':
    main()
