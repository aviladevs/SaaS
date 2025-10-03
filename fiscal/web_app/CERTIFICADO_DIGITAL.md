# 🔐 Sistema de Consulta Automática com Certificado Digital

Sistema completo para consultar automaticamente NFes e CTes na SEFAZ usando certificado digital.

---a

## 🎯 **FUNCIONALIDADES**

### ✅ **Upload de Certificado Digital**
- Upload seguro de certificado A1 (.pfx)
- Validação automática do certificado
- Armazenamento criptografado da senha
- Verificação de validade

### ✅ **Consulta Automática na SEFAZ**
- Busca documentos onde seu CNPJ aparece em **qualquer papel**:
  - 📤 **Emitente** - Documentos que você emitiu
  - 📥 **Destinatário** - Documentos recebidos
  - 🚚 **Transportador** - CTes onde você transportou
  - 👤 **Tomador** - CTes onde você é tomador
  - 📮 **Remetente** - CTes onde você é remetente
  - 📬 **Recebedor** - CTes onde você é recebedor

### ✅ **Interface com Abas**
- Visualização organizada por papel do CNPJ
- Filtros e busca avançada
- Estatísticas em tempo real
- Design mobile-first responsivo

### ✅ **Importação Inteligente**
- Importação individual ou em massa
- Evita duplicatas automaticamente
- Download de XMLs completos
- Export para CSV

### ✅ **Consulta Automática Agendada**
- Configure horário para consultas diárias
- Notificações por email
- Histórico completo de consultas

---

## 🚀 **COMO USAR**

### **1. Adicionar Certificado**

1. Acesse: **Certificados** no menu
2. Clique em **"Adicionar Certificado"**
3. Preencha:
   - Nome do certificado
   - CNPJ
   - Arquivo .pfx
   - Senha do certificado
4. Clique em **"Adicionar Certificado"**

### **2. Consultar SEFAZ**

1. Na lista de certificados, clique em **"Consultar"**
2. Escolha:
   - Tipo de documento (NFe, CTe, NFCe, MDFe)
   - Período (data início e fim)
3. Clique em **"Iniciar Consulta"**
4. Aguarde o processamento

### **3. Visualizar Resultados**

1. Acesse o resultado da consulta
2. Navegue pelas **abas** para ver documentos por papel:
   - **Emitente** - Documentos que você emitiu
   - **Destinatário** - Documentos recebidos
   - **Transportador** - Onde você transportou
   - **Tomador** - Onde você é tomador
   - **Remetente** - Onde você é remetente
   - **Recebedor** - Onde você é recebedor

### **4. Importar Documentos**

**Importação Individual:**
- Clique no botão **verde (download)** ao lado do documento
- Confirme a importação

**Importação em Massa:**
- Clique em **"Importar Todos"**
- Aguarde o processamento

---

## 📋 **REQUISITOS**

### **Certificado Digital**

- **Tipo:** A1 (arquivo .pfx ou .p12)
- **Validade:** Dentro do prazo de validade
- **Emitido por:** Autoridade Certificadora reconhecida (Serasa, Certisign, etc.)

### **Onde Obter**

Certificados digitais são emitidos por Autoridades Certificadoras:
- Serasa Experian
- Certisign
- Valid Certificadora
- Soluti
- AC Safeweb

---

## 🔧 **CONFIGURAÇÕES**

### **Consulta Automática**

1. Acesse: **Configurações > Consulta**
2. Configure:
   - **UFs habilitadas** - Estados para consultar
   - **Horário** - Quando executar consultas automáticas
   - **Email** - Para receber notificações
   - **Limite** - Máximo de documentos por consulta

### **Ativar Consulta Automática**

1. Na lista de certificados
2. Ative o **toggle "Consulta Automática"**
3. O sistema consultará automaticamente no horário configurado

---

## 📊 **DASHBOARD DE CONSULTAS**

Acesse: **Consultas > Dashboard**

Visualize:
- Total de documentos consultados
- Documentos importados
- Documentos pendentes
- Histórico de consultas
- Estatísticas por tipo

---

## 🔐 **SEGURANÇA**

### **Proteção de Dados**

✅ **Certificado criptografado** - Armazenado com criptografia AES-256  
✅ **Senha protegida** - Hash seguro da senha  
✅ **Conexão HTTPS** - Todas as comunicações criptografadas  
✅ **Logs de auditoria** - Registro de todas as consultas  
✅ **Acesso restrito** - Apenas o usuário proprietário acessa  

### **Boas Práticas**

1. ✅ Use senha forte no certificado
2. ✅ Mantenha certificado atualizado
3. ✅ Não compartilhe credenciais
4. ✅ Revise logs regularmente
5. ✅ Configure notificações de email

---

## 📱 **INTERFACE MOBILE**

### **Design Responsivo**

- ✅ **Mobile-First** - Otimizado para celular
- ✅ **Touch-Friendly** - Botões de 48px mínimo
- ✅ **Abas Deslizantes** - Navegação fluida
- ✅ **Tabelas Responsivas** - Scroll horizontal

### **Funciona em:**

- 📱 Smartphones (iOS/Android)
- 📱 Tablets
- 💻 Desktops
- 🖥️ Monitores wide

---

## 🎯 **CASOS DE USO**

### **1. Contador/Escritório Contábil**

**Problema:** Clientes não enviam XMLs  
**Solução:** Consulte automaticamente todos os documentos

**Como:**
1. Cadastre certificado de cada cliente
2. Ative consulta automática
3. Receba notificações diárias
4. Importe XMLs automaticamente

### **2. Empresa com Múltiplas Filiais**

**Problema:** Controlar documentos de várias filiais  
**Solução:** Um certificado por filial

**Como:**
1. Cadastre certificado de cada filial
2. Consulte por período
3. Visualize por papel (emitente, destinatário, etc.)
4. Exporte relatórios

### **3. Transportadora**

**Problema:** Rastrear CTes onde aparece  
**Solução:** Consulta específica de CTes

**Como:**
1. Cadastre certificado
2. Consulte apenas CTes
3. Veja aba "Transportador"
4. Importe CTes relevantes

### **4. Indústria/Comércio**

**Problema:** Conferir NFes de fornecedores  
**Solução:** Consulta de NFes recebidas

**Como:**
1. Cadastre certificado
2. Consulte NFes
3. Veja aba "Destinatário"
4. Confira com pedidos

---

## 🔍 **TIPOS DE DOCUMENTOS**

### **NFe - Nota Fiscal Eletrônica**

Busca onde seu CNPJ aparece como:
- Emitente (vendas)
- Destinatário (compras)

### **CTe - Conhecimento de Transporte**

Busca onde seu CNPJ aparece como:
- Emitente (prestador de serviço)
- Tomador (contratante)
- Remetente (origem da carga)
- Destinatário (destino da carga)
- Expedidor (quem despacha)
- Recebedor (quem recebe)
- Transportador (quem transporta)

### **NFCe - NFC-e**

Nota Fiscal de Consumidor Eletrônica

### **MDFe - Manifesto de Documentos Fiscais**

Manifesto de transporte

---

## 📊 **RELATÓRIOS E EXPORTS**

### **Exportar CSV**

Exporta lista de documentos com:
- Número, série, data
- Emitente e destinatário
- Valores
- Status de importação

### **Baixar XMLs (ZIP)**

Baixa todos os XMLs em arquivo ZIP:
- Organizados por tipo
- Nomeados pela chave de acesso
- Prontos para importação

### **Estatísticas**

- Total por papel
- Valor total por papel
- Documentos por período
- Top emitentes/destinatários

---

## ⚙️ **CONFIGURAÇÕES AVANÇADAS**

### **UFs Habilitadas**

Configure quais estados consultar:
```
SP,RJ,MG,RS,PR,SC,BA,PE,CE
```

### **Timeout**

Tempo máximo de espera por consulta (segundos):
```
Padrão: 300 segundos (5 minutos)
```

### **Max Documentos**

Limite de documentos por consulta:
```
Padrão: 1000 documentos
Recomendado: 500-2000
```

### **Intervalo de Consulta**

Para consultas automáticas (minutos):
```
Padrão: 60 minutos
Mínimo: 30 minutos
```

---

## 🐛 **TROUBLESHOOTING**

### **Erro: "Certificado inválido"**

**Causas:**
- Certificado expirado
- Senha incorreta
- Arquivo corrompido

**Solução:**
1. Verifique validade do certificado
2. Confirme senha
3. Baixe certificado novamente

### **Erro: "Timeout na consulta"**

**Causas:**
- SEFAZ indisponível
- Período muito grande
- Muitos documentos

**Solução:**
1. Reduza período de consulta
2. Tente em outro horário
3. Aumente timeout nas configurações

### **Erro: "Nenhum documento encontrado"**

**Causas:**
- CNPJ não tem movimentação no período
- UF incorreta
- Certificado de outro CNPJ

**Solução:**
1. Verifique se CNPJ está correto
2. Amplie período de busca
3. Verifique UF do certificado

---

## 📞 **SUPORTE**

### **Documentação**

- **Sistema:** `web_app/README.md`
- **Deploy:** `DEPLOY_COMPLETO.md`
- **API:** `web_app/api/README.md`

### **Logs**

Verifique logs de consulta em:
- **Interface:** Consultas > Logs
- **Sistema:** `gcloud app logs tail`

---

## 🎉 **PRONTO!**

Agora você tem um sistema completo de consulta automática de documentos fiscais!

**Recursos:**
✅ Upload seguro de certificados  
✅ Consulta automática na SEFAZ  
✅ Interface com abas por papel  
✅ Importação inteligente  
✅ Consultas agendadas  
✅ Notificações por email  
✅ Export CSV e ZIP  
✅ Mobile-first responsivo  

**Acesse:** https://fiscal.aviladevops.com.br/certificados/

---

**🔐 Consulte, organize e importe seus XMLs automaticamente!**
