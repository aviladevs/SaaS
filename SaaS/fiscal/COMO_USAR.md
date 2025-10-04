# 🚀 COMO USAR - Guia Simples

## 📋 O que você tem agora

Você tem **2 opções** de uso:

### ✅ Opção 1: Scripts Python Simples (RECOMENDADO para começar)
- ✅ Importa XMLs direto para Cloud SQL
- ✅ Gera relatórios
- ✅ Mais simples de usar

### ✅ Opção 2: Sistema Web Completo + API Mobile
- ✅ Interface web responsiva
- ✅ API REST para criar app mobile
- ✅ Dashboard com gráficos
- ✅ Requer mais configuração

---

## 🎯 COMEÇAR RÁPIDO - Opção 1 (Scripts Simples)

### 1️⃣ Testar Conexão Cloud SQL

```powershell
python test_cloudsql_simples.py
```

**O que acontece:**
- ✅ Testa conexão com Google Cloud SQL
- ✅ Mostra tabelas existentes
- ✅ Dá dicas se der erro

### 2️⃣ Importar XMLs

```powershell
python import_to_cloudsql.py
```

**O que acontece:**
- ✅ Lê TODOS os XMLs das pastas NFe/ e CTe/
- ✅ Cria tabelas no banco automaticamente
- ✅ Importa dados estruturados
- ✅ Evita duplicatas
- ✅ Mostra estatísticas

### 3️⃣ Consultar Dados

```powershell
python consultar_dados.py
```

**O que acontece:**
- ✅ Menu interativo
- ✅ Relatórios prontos
- ✅ Estatísticas de vendas
- ✅ Top produtos, emitentes, rotas

---

## 🌐 OPÇÃO 2 - Sistema Web + API Mobile

### Quando usar?
- ✅ Quer interface web bonita
- ✅ Vai criar app mobile (Flutter/React Native)
- ✅ Quer dashboard com gráficos
- ✅ Precisa de API REST

### Setup Rápido

```powershell
cd web_app
pip install Django==4.2.7 djangorestframework==3.14.0 django-cors-headers==4.3.1
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Acesse: http://localhost:8000

### Documentação Completa
- `web_app/README.md` - Guia completo da web
- `INICIO_RAPIDO.md` - Setup detalhado

---

## 📝 Configuração Inicial

### Criar config.json

```json
{
  "host": "34.xxx.xxx.xxx",
  "user": "seu_usuario",
  "password": "sua_senha",
  "database": "xml_fiscais",
  "port": 3306,
  "diretorios": {
    "nfe": "./NFe",
    "cte": "./CTe"
  }
}
```

### Onde pegar essas informações?

#### 1. Host (IP do Cloud SQL)
```
Google Cloud Console > SQL > Sua Instância > Overview
Copie o "Public IP address"
```

#### 2. User e Password
```
Google Cloud Console > SQL > Sua Instância > Users
Crie um usuário ou use root
```

#### 3. Database
```
Conecte ao Cloud SQL e execute:
CREATE DATABASE xml_fiscais CHARACTER SET utf8mb4;
```

---

## 🔧 Configurar Cloud SQL

### Passo 1: Criar Instância (se não tem)

```
1. Acesse: https://console.cloud.google.com/sql
2. Clique em "CREATE INSTANCE"
3. Escolha "MySQL"
4. Configure:
   - Instance ID: xml-manager
   - Password: [sua senha segura]
   - Region: southamerica-east1 (São Paulo)
   - Version: MySQL 8.0
5. Clique em "CREATE INSTANCE"
```

### Passo 2: Configurar Rede

```
1. Vá em: Sua Instância > Connections > Networking
2. Em "Authorized networks" clique "ADD NETWORK"
3. Para testes: 
   - Nome: "Todos"
   - Network: 0.0.0.0/0
   ⚠️ Em produção, use apenas seu IP!
4. Clique "DONE" e "SAVE"
```

### Passo 3: Criar Banco

```
1. Vá em: Sua Instância > Databases
2. Clique "CREATE DATABASE"
3. Nome: xml_fiscais
4. Character set: utf8mb4
5. Collation: utf8mb4_unicode_ci
6. Clique "CREATE"
```

### Passo 4: Criar Usuário

```
1. Vá em: Sua Instância > Users
2. Clique "ADD USER ACCOUNT"
3. Username: xml_user
4. Password: [senha segura]
5. Host: % (permite de qualquer IP)
6. Clique "ADD"
```

---

## 🎯 Fluxo de Trabalho Recomendado

### Para Consulta Rápida:
```
1. python test_cloudsql_simples.py  → Testa conexão
2. python consultar_dados.py        → Ver relatórios
```

### Para Importar Novos XMLs:
```
1. Coloque XMLs nas pastas NFe/ ou CTe/
2. python import_to_cloudsql.py     → Importa tudo
3. python consultar_dados.py        → Verifica dados
```

### Para Usar Interface Web:
```
1. cd web_app
2. python manage.py runserver
3. Abra: http://localhost:8000
4. Login com credenciais criadas
```

### Para Desenvolver App Mobile:
```
1. cd web_app
2. python manage.py runserver
3. Use API REST em: http://localhost:8000/api/
4. Consulte: web_app/README.md para exemplos
```

---

## 📊 Estrutura dos Arquivos

### Scripts Principais (Opção 1)
```
test_cloudsql_simples.py    → Testa conexão
import_to_cloudsql.py       → Importa XMLs
consultar_dados.py          → Relatórios
xml_parser.py               → Parse de XMLs
database_schema.sql         → Schema do banco
config.json                 → Suas credenciais
```

### Sistema Web (Opção 2)
```
web_app/
├── manage.py               → Django command
├── xml_manager/            → Configurações
├── core/                   → App principal
├── api/                    → API REST
└── templates/              → HTML responsivo
```

---

## ❓ Problemas Comuns

### "Can't connect to MySQL server"

**Causa:** Firewall bloqueando  
**Solução:**
```
1. No Cloud SQL, adicione seu IP em "Authorized networks"
2. Ou adicione 0.0.0.0/0 para liberar todos (teste apenas!)
3. Verifique se instância está ATIVA (não pausada)
```

### "Access denied for user"

**Causa:** Senha errada ou usuário sem permissão  
**Solução:**
```
1. Verifique user/password em config.json
2. No Cloud SQL, recrie o usuário
3. Dê permissões: GRANT ALL ON xml_fiscais.* TO 'user'@'%';
```

### "Unknown database"

**Causa:** Banco não criado  
**Solução:**
```
1. No Cloud SQL, crie o banco:
   CREATE DATABASE xml_fiscais CHARACTER SET utf8mb4;
```

### "XMLs não importados"

**Causa:** Formato inválido  
**Solução:**
```
1. Verifique se são XMLs válidos de NFe/CTe
2. Alguns arquivos em "Outros/" podem não ser documentos fiscais
3. O script pula automaticamente arquivos inválidos
```

---

## 📱 Próximos Passos

### Depois que estiver funcionando:

1. **Explorar Dados**
   ```powershell
   python consultar_dados.py
   # Use o menu interativo
   ```

2. **Criar Relatórios Personalizados**
   - Edite `consultar_dados.py`
   - Adicione suas próprias consultas SQL

3. **Interface Web** (opcional)
   ```powershell
   cd web_app
   python manage.py runserver
   ```

4. **App Mobile** (opcional)
   - Leia `web_app/README.md`
   - API REST pronta em `/api/`

---

## 🎓 Aprender Mais

### SQL Direto
```sql
-- Conecte ao Cloud SQL e execute:

-- Ver todas as NFes
SELECT numero_nf, emit_nome, valor_total 
FROM nfe 
ORDER BY data_emissao DESC 
LIMIT 10;

-- Total por emitente
SELECT emit_nome, COUNT(*) as total, SUM(valor_total) as valor
FROM nfe
GROUP BY emit_nome
ORDER BY total DESC;

-- Produtos mais vendidos
SELECT descricao, SUM(quantidade) as qtd
FROM nfe_itens
GROUP BY descricao
ORDER BY qtd DESC
LIMIT 20;
```

### Python Customizado
```python
# Adicione suas próprias consultas em consultar_dados.py
def minha_consulta(self):
    sql = """
        SELECT ... FROM nfe WHERE ...
    """
    cols, results = self.executar_query(sql)
    # Processar resultados
```

---

## ✅ Checklist de Sucesso

- [ ] Cloud SQL criado e configurado
- [ ] config.json criado com credenciais
- [ ] Teste de conexão passou (test_cloudsql_simples.py)
- [ ] XMLs importados com sucesso
- [ ] Relatórios funcionando
- [ ] (Opcional) Sistema web rodando
- [ ] (Opcional) API testada

---

## 🎉 Está Tudo Pronto!

Você tem agora:

✅ **Parser de XMLs** - Lê NFe e CTe  
✅ **Cloud SQL** - Dados na nuvem  
✅ **Scripts Python** - Importação e consultas  
✅ **Sistema Web** - Interface responsiva  
✅ **API REST** - Para app mobile  
✅ **Mobile-First** - Funciona em celular  

**Escolha sua opção e comece a usar! 🚀**

---

## 📞 Dúvidas?

1. Leia os README.md nos diretórios
2. Teste os scripts um por um
3. Verifique os logs de erro
4. Consulte documentação do Google Cloud SQL

**Boa sorte! 🎯**
