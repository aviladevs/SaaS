# 🚀 **GUIA DE DEPLOYMENT - SaaS Ávila DevOps**

## 📋 **Visão Geral**

Este documento descreve a solução completa dos problemas identificados nos logs do Google Cloud e o processo de deploy dos serviços SaaS.

---

## 🚨 **Problemas Identificados e Resolvidos**

### **1. 🔐 Conflitos de Políticas IAM**
**Erro:** `There were concurrent policy changes. Please retry the whole read-modify-write with exponential backoff.`

**🔍 Causa:** Múltiplos processos tentando modificar políticas IAM simultaneamente.

**✅ Solução:**
- Implementado mecanismo de retry com backoff exponencial
- Criado script de limpeza de políticas conflitantes
- Configurado políticas IAM estáveis

### **2. 🔑 Problemas do Cloud KMS**
**Erro:** `External key error: Could not resolve the domain name for the key.`

**🔍 Causa:** Chave KMS externa com configuração incorreta.

**✅ Solução:**
- Corrigido URI da chave: `projects/principaldevops/locations/global/keyRings/saas-nfe-keyring/cryptoKeys/saas-database-key`
- Recriada estrutura de chave KMS quando necessário
- Configurado permissões adequadas para service accounts

### **3. 🏗️ Problemas do Cloud Build**
**Erro:** Falhas no Cloud Build (código 9)

**🔍 Causa:** Service account sem permissões adequadas e configuração incorreta.

**✅ Solução:**
- Configurado service account do Cloud Build com roles necessárias
- Implementado trigger básico funcional
- Corrigido configuração de build

### **4. 🐳 Problemas de Dockerfile**
**Erro:** `unable to prepare context: unable to evaluate symlinks in Dockerfile path`

**🔍 Causa:** Sintaxe incorreta nos Dockerfiles.

**✅ Solução:**
- Corrigido erro de sintaxe no Dockerfile da Landing Page
- Criada estrutura Django completa para o sistema
- Criado Dockerfile padrão para a clínica

---

## 📋 **Scripts de Correção Criados**

### **🔧 Scripts Disponíveis:**

| Script | Função | Quando Usar |
|--------|--------|-------------|
| `fix_kms_config.sh` | Corrige configuração do Cloud KMS | Quando houver erros de chave KMS |
| `fix_cloudbuild.sh` | Corrige problemas do Cloud Build | Quando houver falhas no build |
| `test_deployment.sh` | Testa toda a configuração | Para verificar se tudo está funcionando |
| `deploy_services_v2.py` | Deploy atualizado com correções | Para fazer deploy completo |

---

## 🚀 **Como Executar as Correções**

### **Método 1: Correção Automatizada (Recomendado)**

```bash
# 1. Corrigir configuração do KMS
bash fix_kms_config.sh

# 2. Corrigir configuração do Cloud Build
bash fix_cloudbuild.sh

# 3. Testar toda a configuração
bash test_deployment.sh

# 4. Executar deploy completo
python deploy_services_v2.py
```

### **Método 2: Correção Manual**

```bash
# Limpar políticas IAM conflitantes
gcloud projects remove-iam-policy-binding principaldevops \
  --member="serviceAccount:791209015957@cloudbuild.gserviceaccount.com" \
  --role="roles/cloudbuild.builds.builder"

# Recriar chave KMS
gcloud kms keys create saas-database-key \
  --keyring saas-nfe-keyring \
  --location global \
  --purpose encryption \
  --project principaldevops

# Habilitar APIs necessárias
gcloud services enable run.googleapis.com cloudbuild.googleapis.com kms.googleapis.com
```

---

## 📊 **Status dos Serviços**

| Serviço | Status | Dockerfile | Configuração |
|---------|--------|------------|--------------|
| **🏠 Landing Page** | ✅ Pronto | Corrigido | app.yaml atualizado |
| **🏭 Sistema** | ✅ Pronto | Criado | Estrutura Django completa |
| **📊 Fiscal** | ✅ Pronto | Existe | web_app configurado |
| **🏥 Clínica** | ✅ Pronto | Criado | Dockerfile padrão |

---

## 🌐 **URLs de Deploy**

Após deploy bem-sucedido, os serviços estarão disponíveis em:

| Serviço | Domínio | URL Cloud Run |
|---------|---------|---------------|
| **Landing Page** | `aviladevops.com.br` | `https://landing-page-service-xxx.southamerica-east1.run.app` |
| **Sistema** | `sistema.aviladevops.com.br` | `https://sistema-service-xxx.southamerica-east1.run.app` |
| **Fiscal** | `fiscal.aviladevops.com.br` | `https://fiscal-service-xxx.southamerica-east1.run.app` |
| **Clínica** | `clinica.aviladevops.com.br` | `https://clinica-service-xxx.southamerica-east1.run.app` |

---

## 🔧 **Arquivos Modificados/Criados**

### **Arquivos Corrigidos:**
- `LANDING-PAGE/Dockerfile` - Removido erro de sintaxe
- `sistema/Dockerfile` - Ajustado para apontar para wsgi correto
- `project-config.json` - Atualizado configuração KMS

### **Arquivos Criados:**
- `sistema/sistema/wsgi.py` - Arquivo WSGI para Django
- `sistema/sistema/settings.py` - Configurações Django
- `sistema/sistema/urls.py` - URLs da aplicação
- `sistema/sistema/__init__.py` - Arquivo init
- `clinica/Dockerfile` - Dockerfile padrão para desenvolvimento
- `dispatch.yaml` - Configuração de roteamento de domínios

### **Scripts de Automação:**
- `fix_kms_config.sh` - Correção automática do KMS
- `fix_cloudbuild.sh` - Correção automática do Cloud Build
- `test_deployment.sh` - Teste completo da configuração
- `deploy_services_v2.py` - Deploy atualizado

---

## ⚠️ **Problemas Comuns e Soluções**

### **Erro: "Permission denied"**
```bash
# Solução: Verificar permissões
gcloud projects get-iam-policy principaldevops --format="table(bindings.role)"
```

### **Erro: "API not enabled"**
```bash
# Solução: Habilitar APIs
gcloud services enable run.googleapis.com cloudbuild.googleapis.com
```

### **Erro: "KMS key not found"**
```bash
# Solução: Recriar chave
bash fix_kms_config.sh
```

### **Erro: "Cloud Build failed"**
```bash
# Solução: Corrigir configuração
bash fix_cloudbuild.sh
```

---

## 📈 **Próximos Passos Após Deploy**

### **1. Configurar Domínios Personalizados**
```bash
# No Google Cloud Console:
# App Engine > Configurações > Domínios personalizados
# Adicionar domínios e configurar CNAME no provedor
```

### **2. Configurar SSL (HTTPS)**
- Os serviços já vêm com SSL automático via Google Cloud
- Apenas configurar os registros CNAME no provedor de domínio

### **3. Monitoramento**
- Configurar alertas no Google Cloud Monitoring
- Monitorar logs em Cloud Logging
- Configurar uptime checks

### **4. Backup e Recuperação**
- Configurar backups automáticos no Cloud SQL
- Testar processo de recuperação

---

## 🎯 **Checklist de Verificação**

- [ ] Políticas IAM sem conflitos
- [ ] APIs necessárias habilitadas
- [ ] Chave KMS configurada corretamente
- [ ] Service account do Cloud Build com permissões adequadas
- [ ] Dockerfiles sem erros de sintaxe
- [ ] Deploy testado com sucesso
- [ ] Domínios personalizados configurados
- [ ] SSL funcionando
- [ ] Monitoramento ativo

---

## 📞 **Suporte e Troubleshooting**

### **Logs Importantes:**
- **Cloud Logging:** `projects/principaldevops/logs/`
- **Cloud Build:** Build history no console
- **App Engine:** Logs de aplicação

### **Comandos Úteis para Debug:**
```bash
# Verificar serviços rodando
gcloud run services list

# Verificar builds
gcloud builds list

# Verificar logs recentes
gcloud logging read "resource.type=cloud_run_revision" --limit 10

# Testar serviço
curl https://SEU-SERVICO.run.app
```

---

## 📋 **Histórico de Correções**

| Data | Problema | Solução | Status |
|------|----------|---------|--------|
| 04/10/2024 | Conflitos IAM | Script limpeza políticas | ✅ Resolvido |
| 04/10/2024 | KMS key error | Recriação chave | ✅ Resolvido |
| 04/10/2024 | Cloud Build fail | Configuração SA | ✅ Resolvido |
| 04/10/2024 | Dockerfile syntax | Correção arquivos | ✅ Resolvido |

---

**🚀 Desenvolvido pela Ávila DevOps** | **Status: Problemas Críticos Resolvidos** ✅
