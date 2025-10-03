# 🚀 Status de Deployment - fiscal.aviladevops.com.br

## ✅ Configuração Completa e Verificada

Data da última verificação: 2024

### 📋 Resumo

O sistema está configurado para deploy automático no Google Cloud Platform usando **Cloud Run** com o domínio `fiscal.aviladevops.com.br`.

---

## 🔄 Workflow Configurado

### Cloud Run Multi-Service Deployment
**Arquivo:** `.github/workflows/cloudrun-multi.yml`

**Trigger:** Push para branch `main`

**Serviços Deployados:**
- `app` → app.aviladevops.com.br
- `clinica` → clinica.aviladevops.com.br
- `sistema` → sistema.aviladevops.com.br
- **`fiscal` → fiscal.aviladevops.com.br** ✅

### Configurações do Workflow

```yaml
- service: fiscal
  domain: fiscal.aviladevops.com.br
```

**Variáveis de Ambiente Configuradas:**
- `DJANGO_SETTINGS_MODULE=xml_manager.settings_production` ✅
- `DJANGO_SECRET_KEY` (via secrets)
- `DJANGO_DEBUG=False`
- `ALLOWED_HOSTS` (domínio específico)
- `CSRF_TRUSTED_ORIGINS` (HTTPS do domínio)
- `DB_NAME`, `DB_USER`, `DB_PASS` (Cloud SQL)
- `INSTANCE_CONNECTION_NAME` (Cloud SQL connection)
- `ORCID_ID`

**Recursos:**
- **Região:** southamerica-east1
- **Plataforma:** Cloud Run (managed)
- **Autenticação:** Permitida (allow-unauthenticated)
- **Porta:** 8080
- **Cloud SQL:** Conectado via socket Unix

---

## 🏗️ Configurações de Infraestrutura

### 1. App Engine (Alternativo)
**Arquivo:** `web_app/app.yaml`

```yaml
service: fiscal
runtime: python313
DJANGO_SETTINGS_MODULE: xml_manager.settings_production
```

**Nota:** Esta configuração existe mas não está sendo usada atualmente. O deploy ativo é via Cloud Run.

### 2. Dispatch Rules (App Engine)
**Arquivo:** `web_app/dispatch.yaml`

```yaml
- url: "fiscal.aviladevops.com.br/*"
  service: default
- url: "www.fiscal.aviladevops.com.br/*"
  service: default
```

**Nota:** Dispatch rules são para App Engine. Para Cloud Run, o mapeamento é feito via workflow.

### 3. Dockerfile
**Arquivo:** `web_app/Dockerfile`

- Imagem base: `python:3.11-slim`
- Porta exposta: 8080
- WSGI Server: Gunicorn
- Usuário não-root para segurança

---

## ⚙️ Configurações da Aplicação

### Settings Production
**Arquivo:** `web_app/xml_manager/settings_production.py`

**Hosts Permitidos:**
```python
ALLOWED_HOSTS = [
    '.appspot.com',
    'fiscal.aviladevops.com.br',
    'www.fiscal.aviladevops.com.br',
]
```

**CORS Configurado:**
```python
CORS_ALLOWED_ORIGINS = [
    "https://fiscal.aviladevops.com.br",
    "https://www.fiscal.aviladevops.com.br",
    "capacitor://localhost",
    "ionic://localhost",
]
```

**Segurança:**
- ✅ `DEBUG = False`
- ✅ `SECURE_SSL_REDIRECT = True`
- ✅ `SESSION_COOKIE_SECURE = True`
- ✅ `CSRF_COOKIE_SECURE = True`
- ✅ `SECURE_BROWSER_XSS_FILTER = True`
- ✅ `SECURE_CONTENT_TYPE_NOSNIFF = True`
- ✅ `X_FRAME_OPTIONS = 'DENY'`

---

## 🔒 Workflows de Segurança

### 1. CodeQL
**Arquivo:** `.github/workflows/codeql.yml`

- Análise estática de código Python
- Execução semanal e em PRs
- Identificação de vulnerabilidades

### 2. Trivy Security Scan
**Arquivo:** `.github/workflows/trivy.yml`

- Scan do filesystem (repositório)
- Scan da imagem Docker
- Detecção de vulnerabilidades CRITICAL, HIGH, MEDIUM

---

## 🌐 Configuração DNS Necessária

Para o domínio funcionar corretamente, configure no seu provedor DNS:

```
Tipo: CNAME
Nome: fiscal.aviladevops.com.br
Valor: ghs.googlehosted.com
TTL: 3600
```

Ou o valor específico fornecido pelo Cloud Run após o primeiro deploy.

---

## 📊 Fluxo de Deploy

1. **Developer faz push para `main`**
   ```bash
   git push origin main
   ```

2. **GitHub Actions dispara workflow**
   - Checkout do código
   - Autenticação no GCP
   - Build da imagem Docker
   - Push para Artifact Registry

3. **Deploy para Cloud Run**
   - Deploy do serviço `fiscal`
   - Configuração de variáveis de ambiente
   - Conexão com Cloud SQL
   - Mapeamento de domínio

4. **Aplicação fica disponível em:**
   - https://fiscal.aviladevops.com.br

---

## 🔍 Monitoramento e Logs

### Verificar Status do Deploy
```bash
# Ver serviços Cloud Run
gcloud run services list --region=southamerica-east1

# Ver detalhes do serviço fiscal
gcloud run services describe fiscal --region=southamerica-east1

# Ver logs em tempo real
gcloud run services logs read fiscal --region=southamerica-east1 --tail
```

### Verificar Domínios Mapeados
```bash
gcloud run domain-mappings list --region=southamerica-east1
```

---

## 🐛 Troubleshooting

### Deploy falha
1. Verificar secrets configurados no GitHub:
   - `GCP_SA_KEY`
   - `DJANGO_SECRET_KEY`
   - `DB_NAME`, `DB_USER`, `DB_PASS`
   - `INSTANCE_CONNECTION_NAME`

2. Verificar logs do workflow no GitHub Actions

### Domínio não funciona
1. Verificar configuração DNS
2. Verificar mapeamento no Cloud Run
3. Aguardar propagação DNS (pode levar até 48h)

### Erro 502/503
1. Verificar se Cloud SQL está ativo
2. Verificar connection string
3. Verificar logs da aplicação

---

## 📝 Notas Importantes

1. **Secrets do GitHub:** Todos os secrets sensíveis devem estar configurados no repositório GitHub em Settings > Secrets and variables > Actions

2. **Service Account:** O GCP_SA_KEY deve ter permissões para:
   - Cloud Run Admin
   - Artifact Registry Writer
   - Cloud SQL Client
   - Service Account User

3. **Cloud SQL:** A instância deve estar ativa durante o deploy e runtime

4. **Custos:** Cloud Run cobra por uso (CPU, memória, requisições). Configurar min_instances=0 para desenvolvimento pode economizar.

---

## ✅ Checklist de Verificação

- [x] Workflow configurado com serviço fiscal
- [x] Domínio fiscal.aviladevops.com.br configurado
- [x] DJANGO_SETTINGS_MODULE definido
- [x] ALLOWED_HOSTS incluindo domínio
- [x] CORS configurado
- [x] Security headers habilitados
- [x] Workflows de segurança ativos
- [ ] DNS configurado (verificar com administrador de domínio)
- [ ] Secrets do GitHub configurados
- [ ] Cloud SQL ativo e acessível
- [ ] Primeira execução do workflow bem-sucedida

---

## 📚 Documentação Adicional

- **Deploy Completo:** `DEPLOY_COMPLETO.md`
- **Deploy App Engine:** `web_app/DEPLOY.md`
- **README Principal:** `README.md`
- **README Web App:** `web_app/README.md`

---

**Última atualização:** Revisão completa dos workflows - fiscal.aviladevops.com.br configurado ✅
