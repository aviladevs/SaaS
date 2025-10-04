"""
Serviço de consulta automática na SEFAZ
Integração com webservices da Receita Federal
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import xml.etree.ElementTree as ET
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.backends import default_backend
import base64


class SEFAZConsultaService:
    """Serviço para consultar documentos fiscais na SEFAZ"""
    
    # URLs dos webservices por UF (Produção)
    WEBSERVICES_NFE = {
        'SP': 'https://nfe.fazenda.sp.gov.br/ws/nfestatusservico4.asmx',
        'RJ': 'https://nfe.fazenda.rj.gov.br/ws/nfestatusservico4.asmx',
        'MG': 'https://nfe.fazenda.mg.gov.br/nfe2/services/NFeStatusServico4',
        'RS': 'https://nfe.sefazrs.rs.gov.br/ws/NfeStatusServico/NfeStatusServico4.asmx',
        'PR': 'https://nfe.sefa.pr.gov.br/nfe/NFeStatusServico4',
        'SC': 'https://nfe.svrs.rs.gov.br/ws/NfeStatusServico/NfeStatusServico4.asmx',
        'BA': 'https://nfe.sefaz.ba.gov.br/webservices/NFeStatusServico4/NFeStatusServico4.asmx',
        'PE': 'https://nfe.sefaz.pe.gov.br/nfe-service/services/NFeStatusServico4',
        'CE': 'https://nfe.sefaz.ce.gov.br/nfe2/services/NFeStatusServico4',
    }
    
    WEBSERVICES_CTE = {
        'SP': 'https://nfe.fazenda.sp.gov.br/ws/ctestatusservico.asmx',
        'RJ': 'https://cte.fazenda.rj.gov.br/ws/ctestatusservico.asmx',
        'MG': 'https://cte.fazenda.mg.gov.br/cte/services/CTeStatusServico',
    }
    
    def __init__(self, certificado_pfx: bytes, senha: str):
        """
        Inicializa o serviço com certificado digital
        
        Args:
            certificado_pfx: Bytes do arquivo .pfx
            senha: Senha do certificado
        """
        self.certificado_pfx = certificado_pfx
        self.senha = senha
        self.cert_pem = None
        self.key_pem = None
        self._carregar_certificado()
    
    def _carregar_certificado(self):
        """Carrega e converte certificado PFX para PEM"""
        try:
            # Carregar certificado
            private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(
                self.certificado_pfx,
                self.senha.encode(),
                backend=default_backend()
            )
            
            # Converter para PEM (necessário para requests)
            from cryptography.hazmat.primitives import serialization
            
            self.key_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            self.cert_pem = certificate.public_bytes(
                encoding=serialization.Encoding.PEM
            )
            
        except Exception as e:
            raise Exception(f"Erro ao carregar certificado: {e}")
    
    def consultar_nfe_destinadas(
        self,
        cnpj: str,
        data_inicio: datetime,
        data_fim: datetime,
        uf: str = 'SP'
    ) -> List[Dict]:
        """
        Consulta NFes destinadas ao CNPJ
        
        Args:
            cnpj: CNPJ do destinatário
            data_inicio: Data inicial da consulta
            data_fim: Data final da consulta
            uf: UF para consulta
            
        Returns:
            Lista de dicionários com dados das NFes encontradas
        """
        
        # Montar SOAP envelope
        soap_body = f"""<?xml version="1.0" encoding="UTF-8"?>
        <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
            <soap:Body>
                <nfeDistDFeInteresse xmlns="http://www.portalfiscal.inf.br/nfe">
                    <nfeDadosMsg>
                        <distDFeInt versao="1.01" xmlns="http://www.portalfiscal.inf.br/nfe">
                            <tpAmb>1</tpAmb>
                            <cUFAutor>{self._get_codigo_uf(uf)}</cUFAutor>
                            <CNPJ>{cnpj}</CNPJ>
                            <distNSU>
                                <ultNSU>000000000000000</ultNSU>
                            </distNSU>
                        </distDFeInt>
                    </nfeDadosMsg>
                </nfeDistDFeInteresse>
            </soap:Body>
        </soap:Envelope>"""
        
        try:
            # Fazer requisição com certificado
            response = requests.post(
                self.WEBSERVICES_NFE.get(uf),
                data=soap_body,
                headers={'Content-Type': 'application/soap+xml; charset=utf-8'},
                cert=(self.cert_pem, self.key_pem),
                timeout=60
            )
            
            # Parsear resposta XML
            return self._parsear_resposta_nfe(response.text)
            
        except Exception as e:
            raise Exception(f"Erro na consulta SEFAZ: {e}")
    
    def consultar_nfe_emitidas(
        self,
        cnpj: str,
        data_inicio: datetime,
        data_fim: datetime,
        uf: str = 'SP'
    ) -> List[Dict]:
        """
        Consulta NFes emitidas pelo CNPJ
        
        Similar à consulta de destinadas, mas busca como emitente
        """
        # Implementação similar, mas com filtro de emitente
        pass
    
    def consultar_cte(
        self,
        cnpj: str,
        data_inicio: datetime,
        data_fim: datetime,
        papel: str = 'TODOS',  # EMITENTE, DESTINATARIO, TOMADOR, REMETENTE
        uf: str = 'SP'
    ) -> List[Dict]:
        """
        Consulta CTes onde o CNPJ aparece em qualquer papel
        
        Args:
            cnpj: CNPJ para buscar
            data_inicio: Data inicial
            data_fim: Data final
            papel: Papel do CNPJ (TODOS, EMITENTE, DESTINATARIO, etc)
            uf: UF para consulta
        """
        # Implementação de consulta CTe
        pass
    
    def baixar_xml_completo(self, chave_acesso: str, uf: str = 'SP') -> Optional[str]:
        """
        Baixa XML completo pela chave de acesso
        
        Args:
            chave_acesso: Chave de 44 dígitos
            uf: UF emissora
            
        Returns:
            String com XML completo ou None se erro
        """
        
        soap_body = f"""<?xml version="1.0" encoding="UTF-8"?>
        <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
            <soap:Body>
                <nfeConsultaNF xmlns="http://www.portalfiscal.inf.br/nfe">
                    <nfeDadosMsg>
                        <consSitNFe versao="4.00" xmlns="http://www.portalfiscal.inf.br/nfe">
                            <tpAmb>1</tpAmb>
                            <xServ>CONSULTAR</xServ>
                            <chNFe>{chave_acesso}</chNFe>
                        </consSitNFe>
                    </nfeDadosMsg>
                </nfeConsultaNF>
            </soap:Body>
        </soap:Envelope>"""
        
        try:
            response = requests.post(
                self.WEBSERVICES_NFE.get(uf),
                data=soap_body,
                headers={'Content-Type': 'application/soap+xml; charset=utf-8'},
                cert=(self.cert_pem, self.key_pem),
                timeout=30
            )
            
            # Extrair XML da resposta
            root = ET.fromstring(response.text)
            # Parsear e retornar XML
            return response.text
            
        except Exception as e:
            print(f"Erro ao baixar XML: {e}")
            return None
    
    def _parsear_resposta_nfe(self, xml_response: str) -> List[Dict]:
        """Parseia resposta XML da SEFAZ e extrai dados das NFes"""
        documentos = []
        
        try:
            root = ET.fromstring(xml_response)
            
            # Navegar no XML e extrair dados
            # (Implementação específica depende do formato de resposta da SEFAZ)
            
            for doc in root.findall('.//docZip'):
                # Decodificar e parsear cada documento
                xml_doc = base64.b64decode(doc.text).decode('utf-8')
                dados = self._extrair_dados_nfe(xml_doc)
                if dados:
                    documentos.append(dados)
            
        except Exception as e:
            print(f"Erro ao parsear resposta: {e}")
        
        return documentos
    
    def _extrair_dados_nfe(self, xml_nfe: str) -> Optional[Dict]:
        """Extrai dados principais de uma NFe"""
        try:
            root = ET.fromstring(xml_nfe)
            
            # Namespace NFe
            ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
            
            # Extrair dados
            inf_nfe = root.find('.//nfe:infNFe', ns)
            if not inf_nfe:
                return None
            
            chave = inf_nfe.get('Id', '').replace('NFe', '')
            
            ide = inf_nfe.find('.//nfe:ide', ns)
            emit = inf_nfe.find('.//nfe:emit', ns)
            dest = inf_nfe.find('.//nfe:dest', ns)
            total = inf_nfe.find('.//nfe:total/nfe:ICMSTot', ns)
            
            return {
                'chave_acesso': chave,
                'numero': ide.find('nfe:nNF', ns).text if ide.find('nfe:nNF', ns) is not None else '',
                'serie': ide.find('nfe:serie', ns).text if ide.find('nfe:serie', ns) is not None else '',
                'data_emissao': ide.find('nfe:dhEmi', ns).text if ide.find('nfe:dhEmi', ns) is not None else '',
                'emit_cnpj': emit.find('.//nfe:CNPJ', ns).text if emit.find('.//nfe:CNPJ', ns) is not None else '',
                'emit_nome': emit.find('.//nfe:xNome', ns).text if emit.find('.//nfe:xNome', ns) is not None else '',
                'dest_cnpj': dest.find('.//nfe:CNPJ', ns).text if dest and dest.find('.//nfe:CNPJ', ns) is not None else '',
                'dest_nome': dest.find('.//nfe:xNome', ns).text if dest and dest.find('.//nfe:xNome', ns) is not None else '',
                'valor_total': total.find('nfe:vNF', ns).text if total and total.find('nfe:vNF', ns) is not None else '0',
                'xml_completo': xml_nfe
            }
            
        except Exception as e:
            print(f"Erro ao extrair dados da NFe: {e}")
            return None
    
    def _get_codigo_uf(self, uf: str) -> str:
        """Retorna código da UF para SEFAZ"""
        codigos = {
            'SP': '35', 'RJ': '33', 'MG': '31', 'RS': '43', 'PR': '41',
            'SC': '42', 'BA': '29', 'PE': '26', 'CE': '23', 'GO': '52',
        }
        return codigos.get(uf, '35')
    
    def validar_certificado(self) -> Dict:
        """
        Valida certificado digital
        
        Returns:
            Dict com informações de validade
        """
        try:
            from cryptography import x509
            from cryptography.hazmat.backends import default_backend
            
            cert = x509.load_pem_x509_certificate(self.cert_pem, default_backend())
            
            return {
                'valido': True,
                'validade_inicio': cert.not_valid_before,
                'validade_fim': cert.not_valid_after,
                'emissor': cert.issuer.rfc4514_string(),
                'titular': cert.subject.rfc4514_string(),
            }
        except Exception as e:
            return {
                'valido': False,
                'erro': str(e)
            }
