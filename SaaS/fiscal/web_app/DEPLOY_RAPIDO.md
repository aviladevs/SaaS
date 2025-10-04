# ⚡ DEPLOY RÁPIDO - 3 COMANDOS

## 🚀 Deploy em 3 Minutos

### 1️⃣ Preparar

```powershell
cd "d:\Dev Driver\XML_Organizado\web_app"
python manage.py collectstatic --noinput --settings=xml_manager.settings_production
```

### 2️⃣ Deploy

```powershell
gcloud app deploy app.yaml --quiet
```

### 3️⃣ Abrir

```powershell
gcloud app browse
```

**✅ PRONTO! Seu app está no ar!**

---

## 📋 Primeira Vez?

### Antes do deploy, execute APENAS UMA VEZ:

```powershell
# 1. Login
gcloud auth login

# 2. Definir projeto (substitua PROJECT_ID)
gcloud config set project SEU_PROJECT_ID

# 3. Criar App Engine (escolha região: southamerica-east1)
gcloud app create --region=southamerica-east1

# 4. Habilitar APIs
gcloud services enable appengine.googleapis.com
```

**Agora sim, execute os 3 comandos acima! ⬆️**

---

## 🗄️ Quer usar Cloud SQL?

### Setup Cloud SQL (Opcional)

```powershell
# Criar instância
gcloud sql instances create xml-manager-db ^
  --database-version=MYSQL_8_0 ^
  --tier=db-f1-micro ^
  --region=southamerica-east1 ^
  --root-password=SUA_SENHA

# Criar banco
gcloud sql databases create xml_fiscais ^
  --instance=xml-manager-db ^
  --charset=utf8mb4

# Obter connection name
gcloud sql instances describe xml-manager-db | findstr connectionName
```

Depois, edite `xml_manager/settings_production.py` e descomente a seção `DATABASES`.

---

## 📱 Após o Deploy

### Criar Superusuário

**Via Console Web:**
1. Acesse: https://SEU-APP.appspot.com/admin/
2. Você verá erro (normal na primeira vez)
3. Execute localmente:

```powershell
# Conectar ao Cloud SQL via proxy (se usar Cloud SQL)
# ou criar usuário local e depois replicar

# Criar usuário
python manage.py createsuperuser
```

**Ou via SSH:**
```powershell
gcloud app instances ssh INSTANCE_ID --service=default
python manage.py createsuperuser --settings=xml_manager.settings_production
```

---

## 🔍 Ver Logs

```powershell
gcloud app logs tail -s default
```

---

## 🎯 URLs Importantes

Depois do deploy, acesse:

- **Web App:** https://SEU-PROJECT.appspot.com
- **Admin:** https://SEU-PROJECT.appspot.com/admin/
- **API REST:** https://SEU-PROJECT.appspot.com/api/
- **Dashboard API:** https://SEU-PROJECT.appspot.com/api/dashboard/

---

## ⚙️ Redeploy (Atualizar)

Sempre que fizer mudanças:

```powershell
python manage.py collectstatic --noinput --settings=xml_manager.settings_production
gcloud app deploy app.yaml --quiet
```

---

## 💾 Backup

Ver documentação completa em `DEPLOY.md`

---

## 🐛 Problemas?

### App não inicia
```powershell
gcloud app logs tail -s default
```
Veja o erro nos logs.

### "Application does not exist"
```powershell
gcloud app create --region=southamerica-east1
```

### Static files não carregam
```powershell
python manage.py collectstatic --noinput --clear
gcloud app deploy app.yaml --quiet
```

---

## 💰 Custos

- **App Engine F1:** Grátis (até certo uso)
- **Cloud SQL (opcional):** ~$10/mês

**Total mínimo: GRÁTIS!** (sem Cloud SQL)

---

## 🎉 É isso!

Seu sistema está no ar com:

✅ Interface web responsiva mobile-first  
✅ API REST completa  
✅ HTTPS automático  
✅ Escalamento automático  
✅ Logs em tempo real  

**Documentação completa:** `DEPLOY.md`

---

**Bom deploy! 🚀☁️**
