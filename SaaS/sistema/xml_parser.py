"""
Parser para arquivos XML de NFe e CTe
Extrai os dados estruturados dos XMLs fiscais
"""

import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Optional
import re


class XMLParser:
    """Classe para parsing de XMLs fiscais (NFe e CTe)"""
    
    # Namespaces comuns nos XMLs
    NS_NFE = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
    NS_CTE = {'cte': 'http://www.portalfiscal.inf.br/cte'}
    
    @staticmethod
    def limpar_texto(texto: Optional[str]) -> Optional[str]:
        """Remove espaços extras e caracteres inválidos"""
        if texto is None:
            return None
        return ' '.join(texto.strip().split())
    
    @staticmethod
    def extrair_numero(texto: Optional[str]) -> Optional[float]:
        """Extrai valor numérico de uma string"""
        if not texto:
            return None
        try:
            return float(texto.replace(',', '.'))
        except (ValueError, AttributeError):
            return None
    
    @staticmethod
    def parse_datetime(dt_str: Optional[str]) -> Optional[str]:
        """Converte data ISO para formato MySQL datetime"""
        if not dt_str:
            return None
        try:
            # Remove timezone e converte
            dt_str = re.sub(r'[+-]\d{2}:\d{2}$', '', dt_str)
            dt = datetime.fromisoformat(dt_str)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return None
    
    def parse_nfe(self, xml_path: str) -> Dict:
        """
        Faz parsing de um arquivo NFe
        
        Args:
            xml_path: Caminho para o arquivo XML
            
        Returns:
            Dicionário com os dados estruturados da NFe
        """
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # Tenta encontrar a NFe com e sem namespace
            nfe_elem = root.find('.//nfe:NFe', self.NS_NFE)
            if nfe_elem is None:
                nfe_elem = root.find('.//NFe')
            
            if nfe_elem is None:
                return {'error': 'Estrutura NFe não encontrada no XML'}
            
            # Informações principais
            inf_nfe = nfe_elem.find('.//nfe:infNFe', self.NS_NFE)
            if inf_nfe is None:
                inf_nfe = nfe_elem.find('.//infNFe')
            
            # Chave de acesso
            chave = inf_nfe.get('Id', '').replace('NFe', '')
            
            # Identificação
            ide = inf_nfe.find('.//nfe:ide', self.NS_NFE) or inf_nfe.find('.//ide')
            numero = ide.find('.//nfe:nNF', self.NS_NFE) if ide is not None else None
            if numero is None and ide is not None:
                numero = ide.find('.//nNF')
            serie = ide.find('.//nfe:serie', self.NS_NFE) if ide is not None else None
            if serie is None and ide is not None:
                serie = ide.find('.//serie')
            data_emissao = ide.find('.//nfe:dhEmi', self.NS_NFE) if ide is not None else None
            if data_emissao is None and ide is not None:
                data_emissao = ide.find('.//dhEmi')
            
            # Emitente
            emit = inf_nfe.find('.//nfe:emit', self.NS_NFE) or inf_nfe.find('.//emit')
            emit_data = {}
            if emit is not None:
                emit_data = {
                    'cnpj': self.get_text(emit, 'CNPJ'),
                    'nome': self.get_text(emit, 'xNome'),
                    'fantasia': self.get_text(emit, 'xFant'),
                    'ie': self.get_text(emit, 'IE'),
                }
                
                # Endereço do emitente
                ender_emit = emit.find('.//nfe:enderEmit', self.NS_NFE) or emit.find('.//enderEmit')
                if ender_emit is not None:
                    logradouro = self.get_text(ender_emit, 'xLgr')
                    numero_end = self.get_text(ender_emit, 'nro')
                    bairro = self.get_text(ender_emit, 'xBairro')
                    emit_data['endereco'] = f"{logradouro}, {numero_end} - {bairro}"
                    emit_data['municipio'] = self.get_text(ender_emit, 'xMun')
                    emit_data['uf'] = self.get_text(ender_emit, 'UF')
                    emit_data['cep'] = self.get_text(ender_emit, 'CEP')
            
            # Destinatário
            dest = inf_nfe.find('.//nfe:dest', self.NS_NFE) or inf_nfe.find('.//dest')
            dest_data = {}
            if dest is not None:
                # Tenta CNPJ primeiro, depois CPF
                cnpj_cpf = self.get_text(dest, 'CNPJ')
                if not cnpj_cpf:
                    cnpj_cpf = self.get_text(dest, 'CPF')
                
                dest_data = {
                    'cnpj_cpf': cnpj_cpf,
                    'nome': self.get_text(dest, 'xNome'),
                    'ie': self.get_text(dest, 'IE'),
                }
                
                # Endereço do destinatário
                ender_dest = dest.find('.//nfe:enderDest', self.NS_NFE) or dest.find('.//enderDest')
                if ender_dest is not None:
                    logradouro = self.get_text(ender_dest, 'xLgr')
                    numero_end = self.get_text(ender_dest, 'nro')
                    bairro = self.get_text(ender_dest, 'xBairro')
                    dest_data['endereco'] = f"{logradouro}, {numero_end} - {bairro}"
                    dest_data['municipio'] = self.get_text(ender_dest, 'xMun')
                    dest_data['uf'] = self.get_text(ender_dest, 'UF')
                    dest_data['cep'] = self.get_text(ender_dest, 'CEP')
            
            # Totais
            total = inf_nfe.find('.//nfe:total', self.NS_NFE) or inf_nfe.find('.//total')
            icms_tot = total.find('.//nfe:ICMSTot', self.NS_NFE) if total is not None else None
            if icms_tot is None and total is not None:
                icms_tot = total.find('.//ICMSTot')
            
            valores = {}
            if icms_tot is not None:
                valores = {
                    'valor_total': self.extrair_numero(self.get_text(icms_tot, 'vNF')),
                    'valor_produtos': self.extrair_numero(self.get_text(icms_tot, 'vProd')),
                    'valor_icms': self.extrair_numero(self.get_text(icms_tot, 'vICMS')),
                    'valor_ipi': self.extrair_numero(self.get_text(icms_tot, 'vIPI')),
                    'valor_pis': self.extrair_numero(self.get_text(icms_tot, 'vPIS')),
                    'valor_cofins': self.extrair_numero(self.get_text(icms_tot, 'vCOFINS')),
                    'valor_tributos': self.extrair_numero(self.get_text(icms_tot, 'vTotTrib')),
                }
            
            # Protocolo de autorização
            prot_nfe = root.find('.//nfe:protNFe', self.NS_NFE) or root.find('.//protNFe')
            protocolo_data = {}
            if prot_nfe is not None:
                inf_prot = prot_nfe.find('.//nfe:infProt', self.NS_NFE) or prot_nfe.find('.//infProt')
                if inf_prot is not None:
                    protocolo_data = {
                        'protocolo': self.get_text(inf_prot, 'nProt'),
                        'status': self.get_text(inf_prot, 'cStat'),
                        'motivo': self.get_text(inf_prot, 'xMotivo'),
                    }
            
            # Itens da nota
            itens = []
            for det in inf_nfe.findall('.//nfe:det', self.NS_NFE):
                if det is None:
                    continue
                item = self.parse_nfe_item(det)
                if item:
                    itens.append(item)
            
            # Se não encontrou com namespace, tenta sem
            if not itens:
                for det in inf_nfe.findall('.//det'):
                    item = self.parse_nfe_item(det)
                    if item:
                        itens.append(item)
            
            # XML completo
            xml_content = ET.tostring(root, encoding='unicode')
            
            return {
                'chave_acesso': chave,
                'numero_nf': numero.text if numero is not None else None,
                'serie': serie.text if serie is not None else None,
                'data_emissao': self.parse_datetime(data_emissao.text if data_emissao is not None else None),
                **emit_data,
                **{f'dest_{k}': v for k, v in dest_data.items()},
                **valores,
                **protocolo_data,
                'xml_content': xml_content,
                'itens': itens
            }
            
        except Exception as e:
            return {'error': f'Erro ao processar NFe: {str(e)}'}
    
    def parse_nfe_item(self, det_elem) -> Optional[Dict]:
        """Parse de um item da NFe"""
        try:
            n_item = det_elem.get('nItem')
            if not n_item:
                n_item_elem = det_elem.find('.//nfe:nItem', self.NS_NFE) or det_elem.find('.//nItem')
                n_item = n_item_elem.text if n_item_elem is not None else None
            
            # Produto
            prod = det_elem.find('.//nfe:prod', self.NS_NFE) or det_elem.find('.//prod')
            if prod is None:
                return None
            
            item = {
                'numero_item': int(n_item) if n_item else None,
                'codigo_produto': self.get_text(prod, 'cProd'),
                'descricao': self.get_text(prod, 'xProd'),
                'ncm': self.get_text(prod, 'NCM'),
                'cfop': self.get_text(prod, 'CFOP'),
                'cest': self.get_text(prod, 'CEST'),
                'unidade': self.get_text(prod, 'uCom'),
                'quantidade': self.extrair_numero(self.get_text(prod, 'qCom')),
                'valor_unitario': self.extrair_numero(self.get_text(prod, 'vUnCom')),
                'valor_total': self.extrair_numero(self.get_text(prod, 'vProd')),
                'ean': self.get_text(prod, 'cEAN'),
            }
            
            # Impostos do item
            imposto = det_elem.find('.//nfe:imposto', self.NS_NFE) or det_elem.find('.//imposto')
            if imposto is not None:
                # ICMS
                icms = imposto.find('.//nfe:ICMS', self.NS_NFE) or imposto.find('.//ICMS')
                if icms is not None:
                    for icms_tipo in icms:
                        v_icms = icms_tipo.find('.//nfe:vICMS', self.NS_NFE) or icms_tipo.find('.//vICMS')
                        if v_icms is not None:
                            item['valor_icms'] = self.extrair_numero(v_icms.text)
                            break
                
                # IPI
                ipi = imposto.find('.//nfe:IPI', self.NS_NFE) or imposto.find('.//IPI')
                if ipi is not None:
                    v_ipi = ipi.find('.//nfe:vIPI', self.NS_NFE) or ipi.find('.//vIPI')
                    if v_ipi is not None:
                        item['valor_ipi'] = self.extrair_numero(v_ipi.text)
                
                # PIS
                pis = imposto.find('.//nfe:PIS', self.NS_NFE) or imposto.find('.//PIS')
                if pis is not None:
                    v_pis = pis.find('.//nfe:vPIS', self.NS_NFE) or pis.find('.//vPIS')
                    if v_pis is not None:
                        item['valor_pis'] = self.extrair_numero(v_pis.text)
                
                # COFINS
                cofins = imposto.find('.//nfe:COFINS', self.NS_NFE) or imposto.find('.//COFINS')
                if cofins is not None:
                    v_cofins = cofins.find('.//nfe:vCOFINS', self.NS_NFE) or cofins.find('.//vCOFINS')
                    if v_cofins is not None:
                        item['valor_cofins'] = self.extrair_numero(v_cofins.text)
            
            return item
            
        except Exception as e:
            print(f"Erro ao processar item: {e}")
            return None
    
    def parse_cte(self, xml_path: str) -> Dict:
        """
        Faz parsing de um arquivo CTe
        
        Args:
            xml_path: Caminho para o arquivo XML
            
        Returns:
            Dicionário com os dados estruturados do CTe
        """
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # Tenta encontrar o CTe
            cte_elem = root.find('.//cte:CTe', self.NS_CTE) or root.find('.//CTe')
            if cte_elem is None:
                return {'error': 'Estrutura CTe não encontrada no XML'}
            
            # Informações principais
            inf_cte = cte_elem.find('.//cte:infCte', self.NS_CTE) or cte_elem.find('.//infCte')
            if inf_cte is None:
                return {'error': 'infCte não encontrado'}
            
            # Chave de acesso
            chave = inf_cte.get('Id', '').replace('CTe', '')
            
            # Identificação
            ide = inf_cte.find('.//cte:ide', self.NS_CTE) or inf_cte.find('.//ide')
            ide_data = {}
            if ide is not None:
                ide_data = {
                    'numero_ct': self.get_text(ide, 'nCT'),
                    'serie': self.get_text(ide, 'serie'),
                    'data_emissao': self.parse_datetime(self.get_text(ide, 'dhEmi')),
                    'modal': self.get_text(ide, 'modal'),
                    'tipo_servico': self.get_text(ide, 'tpServ'),
                    'cfop': self.get_text(ide, 'CFOP'),
                    'natureza_operacao': self.get_text(ide, 'natOp'),
                    'municipio_inicio': self.get_text(ide, 'xMunIni'),
                    'uf_inicio': self.get_text(ide, 'UFIni'),
                    'municipio_fim': self.get_text(ide, 'xMunFim'),
                    'uf_fim': self.get_text(ide, 'UFFim'),
                }
            
            # Emitente
            emit = inf_cte.find('.//cte:emit', self.NS_CTE) or inf_cte.find('.//emit')
            emit_data = {}
            if emit is not None:
                emit_data = {
                    'cnpj': self.get_text(emit, 'CNPJ'),
                    'nome': self.get_text(emit, 'xNome'),
                    'fantasia': self.get_text(emit, 'xFant'),
                    'ie': self.get_text(emit, 'IE'),
                }
                
                ender_emit = emit.find('.//cte:enderEmit', self.NS_CTE) or emit.find('.//enderEmit')
                if ender_emit is not None:
                    logradouro = self.get_text(ender_emit, 'xLgr')
                    numero_end = self.get_text(ender_emit, 'nro')
                    bairro = self.get_text(ender_emit, 'xBairro')
                    emit_data['endereco'] = f"{logradouro}, {numero_end} - {bairro}"
                    emit_data['municipio'] = self.get_text(ender_emit, 'xMun')
                    emit_data['uf'] = self.get_text(ender_emit, 'UF')
            
            # Remetente
            rem = inf_cte.find('.//cte:rem', self.NS_CTE) or inf_cte.find('.//rem')
            rem_data = {}
            if rem is not None:
                rem_data = {
                    'cnpj': self.get_text(rem, 'CNPJ'),
                    'nome': self.get_text(rem, 'xNome'),
                    'ie': self.get_text(rem, 'IE'),
                }
                
                ender_rem = rem.find('.//cte:enderReme', self.NS_CTE) or rem.find('.//enderReme')
                if ender_rem is not None:
                    rem_data['municipio'] = self.get_text(ender_rem, 'xMun')
                    rem_data['uf'] = self.get_text(ender_rem, 'UF')
            
            # Destinatário
            dest = inf_cte.find('.//cte:dest', self.NS_CTE) or inf_cte.find('.//dest')
            dest_data = {}
            if dest is not None:
                dest_data = {
                    'cnpj': self.get_text(dest, 'CNPJ'),
                    'nome': self.get_text(dest, 'xNome'),
                    'ie': self.get_text(dest, 'IE'),
                }
                
                ender_dest = dest.find('.//cte:enderDest', self.NS_CTE) or dest.find('.//enderDest')
                if ender_dest is not None:
                    dest_data['municipio'] = self.get_text(ender_dest, 'xMun')
                    dest_data['uf'] = self.get_text(ender_dest, 'UF')
            
            # Valores
            vprest = inf_cte.find('.//cte:vPrest', self.NS_CTE) or inf_cte.find('.//vPrest')
            valores = {}
            if vprest is not None:
                valores['valor_total'] = self.extrair_numero(self.get_text(vprest, 'vTPrest'))
                valores['valor_receber'] = self.extrair_numero(self.get_text(vprest, 'vRec'))
            
            # Valor da carga
            inf_carga = inf_cte.find('.//cte:infCarga', self.NS_CTE) or inf_cte.find('.//infCarga')
            if inf_carga is not None:
                valores['valor_carga'] = self.extrair_numero(self.get_text(inf_carga, 'vCarga'))
            
            # ICMS
            imp = inf_cte.find('.//cte:imp', self.NS_CTE) or inf_cte.find('.//imp')
            if imp is not None:
                icms = imp.find('.//cte:ICMS', self.NS_CTE) or imp.find('.//ICMS')
                if icms is not None:
                    for icms_tipo in icms:
                        v_icms = icms_tipo.find('.//cte:vICMS', self.NS_CTE) or icms_tipo.find('.//vICMS')
                        if v_icms is not None:
                            valores['valor_icms'] = self.extrair_numero(v_icms.text)
                            break
            
            # Protocolo
            prot_cte = root.find('.//cte:protCTe', self.NS_CTE) or root.find('.//protCTe')
            protocolo_data = {}
            if prot_cte is not None:
                inf_prot = prot_cte.find('.//cte:infProt', self.NS_CTE) or prot_cte.find('.//infProt')
                if inf_prot is not None:
                    protocolo_data = {
                        'protocolo': self.get_text(inf_prot, 'nProt'),
                        'status': self.get_text(inf_prot, 'cStat'),
                        'motivo': self.get_text(inf_prot, 'xMotivo'),
                    }
            
            # XML completo
            xml_content = ET.tostring(root, encoding='unicode')
            
            return {
                'chave_acesso': chave,
                **ide_data,
                **{f'emit_{k}': v for k, v in emit_data.items()},
                **{f'rem_{k}': v for k, v in rem_data.items()},
                **{f'dest_{k}': v for k, v in dest_data.items()},
                **valores,
                **protocolo_data,
                'xml_content': xml_content,
            }
            
        except Exception as e:
            return {'error': f'Erro ao processar CTe: {str(e)}'}
    
    def get_text(self, parent, tag_name: str) -> Optional[str]:
        """Obtém o texto de um elemento, tentando com e sem namespace"""
        if parent is None:
            return None
        
        # Tenta com namespace NFe
        elem = parent.find(f'.//nfe:{tag_name}', self.NS_NFE)
        if elem is not None and elem.text:
            return self.limpar_texto(elem.text)
        
        # Tenta com namespace CTe
        elem = parent.find(f'.//cte:{tag_name}', self.NS_CTE)
        if elem is not None and elem.text:
            return self.limpar_texto(elem.text)
        
        # Tenta sem namespace
        elem = parent.find(f'.//{tag_name}')
        if elem is not None and elem.text:
            return self.limpar_texto(elem.text)
        
        return None
