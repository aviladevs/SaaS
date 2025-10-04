# 🚀 GUIA COMPLETO DE DEPLOY

Sistema XML Manager - Deploy no Google Cloud Platform

---

## 📋 VISÃO GERAL

Você tem **3 opções** de deploy:

### 1️⃣ Deploy Web Simples (SQLite)
- ✅ Mais rápido
- ✅ Grátis (free tier)
- ✅ Perfeito para testes
- ❌ Dados resetam a cada deploy

### 2️⃣ Deploy Web + Cloud SQL
- ✅ Banco persistente
- ✅ Produção completa
- ✅ Escalável
- 💰 ~$10/mês

### 3️⃣ Deploy Full (Web + API + Cloud SQL)
- ✅ Tudo incluído
- ✅ API REST para app mobile
- ✅ Interface web moderna
- 💰 ~$10-60/mês

---

## ⚡ OPÇÃO 1: Deploy Rápido (SQLite)

### Pré-requisitos

1. **Google Cloud SDK instalado**
   - Download: https://cloud.google.com/sdk/docs/install
   - Execute o instalador
   - Reinicie terminal

2. **Conta Google Cloud**
   - Crie em: https://console.cloud.google.com
   - Ative billing (cartão necessário, mas tem $300 grátis)

### Passo a Passo

```powershell
# 1. Navegar para pasta web
cd "d:\Dev Driver\XML_Organizado\web_app"

# 2. Verificar se está tudo pronto
python check_deploy.py

# 3. Login (abre navegador)
gcloud auth login

# 4. Listar projetos
gcloud projects list

# 5. Definir projeto ativo
gcloud config set project SEU_PROJECT_ID

# 6. Criar App Engine (APENAS PRIMEIRA VEZ)
gcloud app create --region=southamerica-east1

# 7. Coletar arquivos estáticos
python manage.py collectstatic --noinput --settings=xml_manager.settings_production

# 8. DEPLOY!
gcloud app deploy app.yaml --quiet

# 9. Abrir no navegador
gcloud app browse
```

**✅ PRONTO! Seu app está no ar em 5 minutos!**

URL: https://SEU-PROJECT.appspot.com

---

## 🗄️ OPÇÃO 2: Deploy com Cloud SQL

### Quando usar?
- ✅ Dados persistentes (não perdem no redeploy)
- ✅ Produção real
- ✅ Múltiplos usuários

### Setup Cloud SQL

```powershell
# 1. Criar instância Cloud SQL
gcloud sql instances create xml-manager-db ^
  --database-version=MYSQL_8_0 ^
  --tier=db-f1-micro ^
  --region=southamerica-east1 ^
  --root-password=SENHA_SEGURA_AQUI

# 2. Criar banco de dados
gcloud sql databases create xml_fiscais ^
  --instance=xml-manager-db ^
  --charset=utf8mb4

# 3. Obter connection name
gcloud sql instances describe xml-manager-db | findstr connectionName
```

Você verá algo como: `seu-project:southamerica-east1:xml-manager-db`

### Configurar App

**Edite `xml_manager/settings_production.py`:**

Descomente a seção `DATABASES` e configure:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'xml_fiscais',
        'USER': 'root',
        'PASSWORD': 'SUA_SENHA_AQUI',
        'HOST': '/cloudsql/seu-project:southamerica-east1:xml-manager-db',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        }
    }
}
```

**Edite `app.yaml`:**

Adicione no final:

```yaml
beta_settings:
  cloud_sql_instances: seu-project:southamerica-east1:xml-manager-db

env_variables:
  DB_PASSWORD: 'SUA_SENHA_AQUI'
```

### Deploy

```powershell
# Coletar estáticos
python manage.py collectstatic --noinput --settings=xml_manager.settings_production

# Deploy
gcloud app deploy app.yaml --quiet

# Abrir
gcloud app browse
```

### Executar Migrações

**Opção A: Via Cloud Shell**
```bash
# No console web, abra Cloud Shell e execute:
gcloud sql connect xml-manager-db --user=root
# Digite a senha
USE xml_fiscais;
exit
```

Depois localmente:
```powershell
python manage.py migrate --settings=xml_manager.settings_production
```

**Opção B: Acesse /admin/ e Django cria automaticamente**

---

## 🎯 OPÇÃO 3: Deploy Completo (Web + API)

Mesmos passos da Opção 2, mas:

### Configurações Extras

**1. Configurar CORS para Mobile**

Edite `xml_manager/settings_production.py`:

```python
CORS_ALLOWED_ORIGINS = [
    "https://seu-projeto.appspot.com",
    "capacitor://localhost",
    "ionic://localhost",
]
```

**2. Habilitar Token Authentication**

Já está configurado! Use `/api/auth/login/` para obter token.

**3. Testar API**

```powershell
# Login
curl -X POST https://seu-app.appspot.com/api/auth/login/ ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"admin\",\"password\":\"senha\"}"

# Dashboard
curl https://seu-app.appspot.com/api/dashboard/ ^
  -H "Authorization: Token SEU_TOKEN_AQUI"
```

---

## 👤 CRIAR SUPERUSUÁRIO

### Método 1: Localmente antes do deploy

```powershell
# Configure DATABASES para apontar para Cloud SQL
python manage.py createsuperuser --settings=xml_manager.settings_production
```

### Método 2: Via SSH após deploy

```powershell
# Listar instâncias
gcloud app instances list

# SSH na instância
gcloud app instances ssh INSTANCE_ID --service=default

# Dentro da VM
cd /srv
python manage.py createsuperuser --settings=xml_manager.settings_production
```

### Método 3: Criar manualmente no banco

```sql
# Conecte ao Cloud SQL
gcloud sql connect xml-manager-db --user=root

USE xml_fiscais;

INSERT INTO auth_user (username, password, is_superuser, is_staff, is_active, date_joined)
VALUES ('admin', 'pbkdf2_sha256$...', 1, 1, 1, NOW());
```

(Use Django para gerar hash da senha)

---

## 📊 APÓS O DEPLOY

### Verificar Status

```powershell
# Status geral
gcloud app describe

# Versões
gcloud app versions list

# Logs em tempo real
gcloud app logs tail -s default
```

### URLs Importantes

- **App Principal:** https://SEU-PROJECT.appspot.com
- **Login:** https://SEU-PROJECT.appspot.com/login/
- **Admin:** https://SEU-PROJECT.appspot.com/admin/
- **API:** https://SEU-PROJECT.appspot.com/api/
- **API Docs:** https://SEU-PROJECT.appspot.com/api/

### Testar Funcionalidades

1. ✅ Acesse a URL principal
2. ✅ Faça login
3. ✅ Veja dashboard
4. ✅ Teste API REST
5. ✅ Verifique responsividade mobile

---

## 📱 CONFIGURAR APP MOBILE

### No seu App (Flutter/React Native):

```javascript
// Configuração base
const API_URL = 'https://seu-projeto.appspot.com/api';

// Login
const login = async (username, password) => {
  const response = await fetch(`${API_URL}/auth/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  const data = await response.json();
  return data.token;
};

// Usar token
const getDashboard = async (token) => {
  const response = await fetch(`${API_URL}/dashboard/`, {
    headers: { 'Authorization': `Token ${token}` }
  });
  return response.json();
};
```

---

## 🔍 MONITORAMENTO

### Logs

```powershell
# Tempo real
gcloud app logs tail -s default

# Últimas 100 linhas
gcloud app logs read --limit=100

# Filtrar por erro
gcloud app logs read --severity=ERROR
```

### Métricas no Console

1. Acesse: https://console.cloud.google.com/appengine
2. Clique em sua aplicação
3. Veja gráficos de:
   - Requisições/segundo
   - Latência
   - Erros
   - Uso de memória

### Alertas

Configure em: https://console.cloud.google.com/monitoring

---

## 🔄 ATUALIZAR APP (Redeploy)

```powershell
# 1. Fazer suas alterações no código

# 2. Coletar estáticos
python manage.py collectstatic --noinput --settings=xml_manager.settings_production

# 3. Deploy
gcloud app deploy app.yaml --quiet

# Ou use o script:
deploy.bat
```

---

## 🎛️ GESTÃO E MANUTENÇÃO

### Parar App (economizar custos)

```powershell
# Ver versões
gcloud app versions list

# Parar versão
gcloud app versions stop VERSION_ID
```

### Deletar Versão Antiga

```powershell
gcloud app versions delete VERSION_ID
```

### Escalar Manualmente

Edite `app.yaml`:
```yaml
automatic_scaling:
  min_instances: 2
  max_instances: 20
```

Deploy novamente.

### Backup Cloud SQL

```powershell
# Backup manual
gcloud sql backups create --instance=xml-manager-db

# Listar backups
gcloud sql backups list --instance=xml-manager-db

# Restaurar backup
gcloud sql backups restore BACKUP_ID --backup-instance=xml-manager-db
```

---

## 💰 CUSTOS ESTIMADOS

### Configuração Mínima (Teste/Dev)
- App Engine F1: **Grátis** (free tier)
- Cloud SQL db-f1-micro: **~$7/mês**
- **Total: ~$7/mês**

### Configuração Média (Produção Pequena)
- App Engine F2: **~$35/mês**
- Cloud SQL db-g1-small: **~$25/mês**
- **Total: ~$60/mês**

### Configuração Grande (Produção)
- App Engine F4: **~$120/mês**
- Cloud SQL db-n1-standard-1: **~$150/mês**
- **Total: ~$270/mês**

### Como Economizar
1. Use free tier quando possível
2. Pause Cloud SQL quando não usar
3. Delete versões antigas
4. Configure `min_instances: 0` em dev
5. Use escalamento automático conservador

---

## 🐛 TROUBLESHOOTING

### Erro: "Application does not exist"

```powershell
gcloud app create --region=southamerica-east1
```

### Erro: "Could not connect to CloudSQL"

Verifique:
1. Connection name correto em `app.yaml`
2. Instância Cloud SQL está **ativa** (não pausada)
3. Senha correta

```powershell
# Ver status
gcloud sql instances describe xml-manager-db

# Reiniciar
gcloud sql instances restart xml-manager-db
```

### Erro: "Static files not found"

```powershell
python manage.py collectstatic --noinput --clear
gcloud app deploy app.yaml --quiet
```

### Site lento

1. Aumente `instance_class` em `app.yaml`:
   ```yaml
   instance_class: F4
   ```

2. Configure warm-up requests

3. Aumente tier do Cloud SQL

### Erro 500

```powershell
# Ver logs detalhados
gcloud app logs tail -s default
```

Geralmente é problema de configuração:
- Verifique `settings_production.py`
- Verifique variáveis em `app.yaml`
- Verifique conexão com banco

---

## 🔐 SEGURANÇA

### Checklist de Segurança

- [x] `DEBUG = False` em produção ✅
- [x] `SECRET_KEY` único e forte ✅
- [x] `ALLOWED_HOSTS` configurado ✅
- [x] HTTPS forçado ✅
- [ ] Senha forte no Cloud SQL
- [ ] Backup automático habilitado
- [ ] CORS configurado corretamente
- [ ] Token authentication para API

### Gerar Nova Secret Key

```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Adicione em `app.yaml`:
```yaml
env_variables:
  DJANGO_SECRET_KEY: 'cole_aqui_a_key_gerada'
```

---

## 📚 DOCUMENTAÇÃO ADICIONAL

- **Setup Rápido:** `DEPLOY_RAPIDO.md`
- **Deploy Detalhado:** `web_app/DEPLOY.md`
- **API REST:** `web_app/README.md`
- **Como Usar:** `COMO_USAR.md`

---

## ✅ CHECKLIST FINAL

Antes de considerar deployment completo:

- [ ] App acessível via HTTPS
- [ ] Login funciona
- [ ] Dashboard carrega
- [ ] Superusuário criado
- [ ] API REST testada (se usar)
- [ ] Dados importados (opcional)
- [ ] Logs sem erros críticos
- [ ] Mobile testado (se for usar)
- [ ] Backup configurado
- [ ] Custos monitorados

---

## 🎉 PRONTO!

Seu sistema está no ar com:

✅ **Interface Web Responsiva** - Mobile-first design  
✅ **API REST Completa** - Para app mobile  
✅ **HTTPS Automático** - Segurança SSL  
✅ **Escalamento Automático** - Cresce com demanda  
✅ **Cloud SQL** - Banco persistente (opcional)  
✅ **Logs em Tempo Real** - Monitoramento completo  

---

**Parabéns pelo deploy! 🚀☁️**
