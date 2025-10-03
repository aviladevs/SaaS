# 🚀 DEPLOY NO GOOGLE CLOUD PLATFORM

Guia completo para deploy do XML Manager no GCP.

---

## 📋 PRÉ-REQUISITOS

### 1. Google Cloud SDK Instalado

Verifique se está instalado:
```powershell
gcloud --version
```

Se não estiver, instale:
- Download: https://cloud.google.com/sdk/docs/install
- Execute o instalador
- Reinicie o terminal

### 2. Login no Google Cloud

```powershell
gcloud auth login
```

### 3. Configurar Projeto

```powershell
# Listar projetos
gcloud projects list

# Definir projeto ativo
gcloud config set project SEU_PROJECT_ID

# Verificar
gcloud config get-value project
```

### 4. Habilitar APIs Necessárias

```powershell
gcloud services enable appengine.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

---

## 🎯 OPÇÕES DE DEPLOY

### **Opção 1: Deploy Simples (SQLite)** ⚡

Para testar rapidamente sem banco Cloud SQL.

```powershell
# Coletar estáticos
python manage.py collectstatic --noinput --settings=xml_manager.settings_production

# Deploy
gcloud app deploy app.yaml --quiet
```

**✅ Pronto! Acesse:**
```powershell
gcloud app browse
```

### **Opção 2: Deploy Completo (Cloud SQL)** 🗄️

Para produção com banco de dados na nuvem.

---

## 🗄️ CONFIGURAR CLOUD SQL (Opção 2)

### Passo 1: Criar Instância Cloud SQL

```powershell
gcloud sql instances create xml-manager-db \
  --database-version=MYSQL_8_0 \
  --tier=db-f1-micro \
  --region=southamerica-east1 \
  --root-password=SUA_SENHA_SEGURA
```

**Ou via Console:**
1. Acesse: https://console.cloud.google.com/sql
2. Clique "CREATE INSTANCE" > "MySQL"
3. Configure:
   - Instance ID: `xml-manager-db`
   - Password: [senha segura]
   - Region: `southamerica-east1`
   - Machine: `Shared core - 1 vCPU, 0.614 GB`
4. Clique "CREATE INSTANCE"

### Passo 2: Criar Banco de Dados

```powershell
gcloud sql databases create xml_fiscais \
  --instance=xml-manager-db \
  --charset=utf8mb4
```

### Passo 3: Obter Connection Name

```powershell
gcloud sql instances describe xml-manager-db | findstr connectionName
```

Copie algo como: `project-id:region:xml-manager-db`

### Passo 4: Configurar App para Usar Cloud SQL

Edite `xml_manager/settings_production.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'xml_fiscais',
        'USER': 'root',
        'PASSWORD': os.environ.get('DB_PASSWORD', 'sua_senha'),
        'HOST': '/cloudsql/PROJECT_ID:REGION:xml-manager-db',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        }
    }
}
```

### Passo 5: Adicionar no app.yaml

Adicione em `app.yaml`:

```yaml
env_variables:
  DB_PASSWORD: 'sua_senha_segura'

beta_settings:
  cloud_sql_instances: PROJECT_ID:REGION:xml-manager-db
```

### Passo 6: Deploy

```powershell
gcloud app deploy app.yaml --quiet
```

### Passo 7: Executar Migrações

Depois do deploy, execute as migrações:

**Opção A: Via Cloud Shell**
```bash
gcloud sql connect xml-manager-db --user=root
# Digite a senha
USE xml_fiscais;
# Saia do MySQL
exit
```

Depois, no seu terminal local:
```powershell
python manage.py migrate --settings=xml_manager.settings_production
```

**Opção B: Via Admin**
1. Acesse: https://SEU-APP.appspot.com/admin/
2. Django criará as tabelas automaticamente no primeiro acesso

---

## 🔧 CONFIGURAÇÃO AVANÇADA

### Variáveis de Ambiente

Adicione em `app.yaml` seção `env_variables`:

```yaml
env_variables:
  DJANGO_SECRET_KEY: 'sua-chave-secreta-aqui'
  DB_NAME: 'xml_fiscais'
  DB_USER: 'root'
  DB_PASSWORD: 'senha_segura'
  ALLOWED_HOSTS: '.appspot.com,seudominio.com'
```

### Gerar Secret Key

```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Domínio Customizado

```powershell
# Mapear domínio
gcloud app domain-mappings create seudominio.com

# Verificar
gcloud app domain-mappings list
```

Adicione os registros DNS conforme instruções do console.

---

## 📊 APÓS O DEPLOY

### 1. Criar Superusuário

**Via Console:**
```powershell
gcloud app instances list

# SSH na instância
gcloud app instances ssh INSTANCE_ID --service=default

# Dentro da instância
python manage.py createsuperuser --settings=xml_manager.settings_production
```

**Ou localmente conectando ao Cloud SQL:**
```powershell
# Configurar proxy
cloud_sql_proxy -instances=PROJECT:REGION:INSTANCE=tcp:3306

# Em outro terminal
python manage.py createsuperuser
```

### 2. Importar Dados Existentes

Se já tem dados no Cloud SQL local:

```powershell
# Exportar do banco local
mysqldump -u root -p xml_fiscais > backup.sql

# Importar no Cloud SQL
gcloud sql import sql xml-manager-db gs://BUCKET/backup.sql --database=xml_fiscais
```

### 3. Testar API

```powershell
# Login
curl -X POST https://SEU-APP.appspot.com/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"senha"}'

# Dashboard
curl https://SEU-APP.appspot.com/api/dashboard/ \
  -H "Authorization: Token SEU_TOKEN"
```

---

## 🔍 MONITORAMENTO

### Ver Logs em Tempo Real

```powershell
gcloud app logs tail -s default
```

### Ver Logs no Console

1. Acesse: https://console.cloud.google.com/logs
2. Filtre por: `resource.type="gae_app"`

### Métricas

```powershell
# Abrir métricas
gcloud app open-console --logs
```

---

## 🎛️ GESTÃO DO APP

### Ver Status

```powershell
gcloud app describe
```

### Ver Versões

```powershell
gcloud app versions list
```

### Parar Versão (para economizar)

```powershell
gcloud app versions stop VERSION_ID
```

### Deletar Versão Antiga

```powershell
gcloud app versions delete VERSION_ID
```

### Escalar App

Edite `app.yaml`:
```yaml
automatic_scaling:
  min_instances: 2
  max_instances: 20
```

Depois faça redeploy.

---

## 💰 CUSTOS

### Estimativa Mensal

**Configuração Mínima:**
- App Engine (F1): ~$0 (free tier)
- Cloud SQL (db-f1-micro): ~$7-10/mês
- **Total: ~$10/mês**

**Configuração Recomendada:**
- App Engine (F2): ~$35/mês
- Cloud SQL (db-g1-small): ~$25/mês
- **Total: ~$60/mês**

### Dicas para Economizar

1. **Use free tier quando possível**
2. **Pause Cloud SQL** quando não usar:
   ```powershell
   gcloud sql instances patch xml-manager-db --activation-policy=NEVER
   ```
3. **Monitore uso** no Console
4. **Configure alerts** de budget

---

## 🐛 TROUBLESHOOTING

### Erro: "The Appspot URL does not exist"

**Solução:**
```powershell
# Inicializar App Engine
gcloud app create --region=southamerica-east1
```

### Erro: "Could not connect to CloudSQL"

**Causas comuns:**
1. Connection name errado em `app.yaml`
2. Instância Cloud SQL parada
3. Senha incorreta

**Solução:**
```powershell
# Verificar instância
gcloud sql instances describe xml-manager-db

# Reiniciar se necessário
gcloud sql instances restart xml-manager-db
```

### Erro: "Static files not found"

**Solução:**
```powershell
# Coletar estáticos novamente
python manage.py collectstatic --noinput --clear

# Redeploy
gcloud app deploy app.yaml --quiet
```

### Erro: "Application error"

**Verificar logs:**
```powershell
gcloud app logs tail -s default
```

Geralmente é problema de configuração. Verifique:
1. `settings_production.py`
2. Variáveis em `app.yaml`
3. Banco de dados conectado

### Site muito lento

**Soluções:**
1. Aumentar `instance_class` em `app.yaml`:
   ```yaml
   instance_class: F4
   ```
2. Aumentar `min_instances`:
   ```yaml
   min_instances: 2
   ```
3. Upgrade Cloud SQL tier

---

## 📱 CONFIGURAR PARA APP MOBILE

### 1. Atualizar CORS

Em `settings_production.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "https://seu-app.appspot.com",
    "capacitor://localhost",  # Para Capacitor
    "ionic://localhost",      # Para Ionic
]
```

### 2. Configurar App para Usar API Cloud

No seu app mobile:
```javascript
const API_URL = 'https://seu-app.appspot.com/api';
```

### 3. Testar Endpoints

```powershell
curl https://seu-app.appspot.com/api/dashboard/ \
  -H "Authorization: Token SEU_TOKEN"
```

---

## 🔐 SEGURANÇA EM PRODUÇÃO

### Checklist

- [ ] `DEBUG = False` em produção
- [ ] `SECRET_KEY` diferente do dev
- [ ] `ALLOWED_HOSTS` configurado
- [ ] HTTPS forçado
- [ ] Senha forte no Cloud SQL
- [ ] Backup automático habilitado
- [ ] Firewall rules configuradas
- [ ] CORS restrito a domínios específicos

### Habilitar Backup Automático

```powershell
gcloud sql instances patch xml-manager-db \
  --backup-start-time=03:00 \
  --enable-bin-log
```

### Configurar Firewall

```powershell
gcloud app firewall-rules create 1000 \
  --action=allow \
  --source-range=0.0.0.0/0 \
  --description="Allow all"
```

---

## 📊 PRÓXIMOS PASSOS APÓS DEPLOY

1. **Acessar o app:**
   ```powershell
   gcloud app browse
   ```

2. **Criar superusuário** (veja seção acima)

3. **Importar XMLs:**
   - Configure script local para usar Cloud SQL
   - Execute `import_to_cloudsql.py`

4. **Testar API REST**

5. **Configurar domínio customizado** (opcional)

6. **Configurar monitoramento e alertas**

7. **Desenvolver app mobile** usando a API

---

## 🧩 Adicionar favicon (evitar 404 em /favicon.ico)

- **Onde colocar o arquivo:** adicione seu ícone em `web_app/static/favicon.ico`.
- **Coletar estáticos para produção:**
  ```powershell
  python manage.py collectstatic --noinput --settings=xml_manager.settings_production
  ```
- **Deploy:**
  ```powershell
  gcloud app deploy web_app/app.yaml --quiet
  ```
- **Como funciona:** `app.yaml` já possui um handler dedicado para o favicon e para estáticos:
  - `- url: /static` → serve `staticfiles/`
  - `- url: /favicon\.ico` → serve `staticfiles/favicon.ico`
  Portanto, após o `collectstatic`, o arquivo será servido em produção sem gerar 404.

---

## 🎉 COMANDOS RÁPIDOS

```powershell
# Deploy rápido
gcloud app deploy app.yaml --quiet

# Ver logs
gcloud app logs tail -s default

# Abrir app
gcloud app browse

# Ver versões
gcloud app versions list

# Parar versão antiga
gcloud app versions stop OLD_VERSION

# Ver custo atual
gcloud billing accounts list
```

---

## 📞 SUPORTE

- **Documentação GCP:** https://cloud.google.com/appengine/docs
- **Status:** https://status.cloud.google.com
- **Suporte:** https://cloud.google.com/support

---

**Deploy pronto! Seu sistema está na nuvem! ☁️🚀**
