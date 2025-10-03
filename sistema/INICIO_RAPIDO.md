# 🚀 INÍCIO RÁPIDO - XML Manager

Sistema completo de gestão de XMLs fiscais com interface web responsiva e API REST para app mobile.

## ⚡ Setup em 3 Passos

### 1️⃣ Instalar Dependências

```powershell
cd "d:\Dev Driver\XML_Organizado\web_app"
pip install -r requirements.txt
```

### 2️⃣ Configurar Sistema

```powershell
python setup.py
```

Este comando irá:
- ✅ Criar banco de dados SQLite
- ✅ Fazer migrações
- ✅ Criar superusuário (admin/admin123)
- ✅ Configurar sistema

### 3️⃣ Iniciar Servidor

```powershell
python manage.py runserver
```

**Pronto!** Acesse: http://localhost:8000

---

## 🎯 Acesso Rápido

| Recurso | URL | Credenciais |
|---------|-----|-------------|
| **Web Interface** | http://localhost:8000 | admin / admin123 |
| **Admin Django** | http://localhost:8000/admin/ | admin / admin123 |
| **API REST** | http://localhost:8000/api/ | Token required |

---

## 📱 Testar API REST

### 1. Obter Token de Autenticação

```powershell
# PowerShell
$body = @{
    username = "admin"
    password = "admin123"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login/" -Method POST -Body $body -ContentType "application/json"
$token = $response.token
Write-Host "Token: $token"
```

### 2. Usar API com Token

```powershell
# Dashboard
$headers = @{
    Authorization = "Token $token"
}

Invoke-RestMethod -Uri "http://localhost:8000/api/dashboard/" -Headers $headers
```

### 3. Testar com cURL (Git Bash)

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Dashboard (substitua SEU_TOKEN)
curl http://localhost:8000/api/dashboard/ \
  -H "Authorization: Token SEU_TOKEN"

# Lista NFes
curl http://localhost:8000/api/nfe/ \
  -H "Authorization: Token SEU_TOKEN"
```

---

## 📊 Importar XMLs para o Sistema

### Opção 1: Via Script Python (Recomendado)

```powershell
cd "d:\Dev Driver\XML_Organizado"
python import_to_cloudsql.py
```

### Opção 2: Via Admin Django

1. Acesse http://localhost:8000/admin/
2. Login: admin / admin123
3. Adicione NFes/CTes manualmente

---

## 📱 Desenvolver App Mobile

### Endpoints Principais

```
POST   /api/auth/login/          # Login (retorna token)
GET    /api/dashboard/           # Estatísticas gerais
GET    /api/nfe/                 # Lista NFes
GET    /api/nfe/{id}/            # Detalhes NFe
GET    /api/cte/                 # Lista CTes
GET    /api/cte/{id}/            # Detalhes CTe
GET    /api/statistics/          # Análises
GET    /api/search/?q=termo      # Busca unificada
```

### Exemplo Flutter

```dart
// lib/services/api_service.dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class ApiService {
  static const String baseUrl = 'http://SEU_IP:8000/api';
  String? token;
  
  Future<bool> login(String username, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'username': username,
        'password': password,
      }),
    );
    
    if (response.statusCode == 200) {
      token = jsonDecode(response.body)['token'];
      return true;
    }
    return false;
  }
  
  Future<Map<String, dynamic>> getDashboard() async {
    final response = await http.get(
      Uri.parse('$baseUrl/dashboard/'),
      headers: {'Authorization': 'Token $token'},
    );
    return jsonDecode(response.body);
  }
}
```

### Exemplo React Native

```javascript
// services/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://SEU_IP:8000/api',
});

export const login = async (username, password) => {
  const response = await api.post('/auth/login/', {
    username,
    password,
  });
  const token = response.data.token;
  api.defaults.headers.common['Authorization'] = `Token ${token}`;
  return token;
};

export const getDashboard = () => api.get('/dashboard/');
export const getNFes = (search = '') => api.get('/nfe/', { params: { search } });
```

---

## 🔧 Configuração Avançada

### Usar Google Cloud SQL

Edite `web_app/xml_manager/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'xml_fiscais',
        'USER': 'seu_usuario',
        'PASSWORD': 'sua_senha',
        'HOST': '34.xxx.xxx.xxx',  # IP do Cloud SQL
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        }
    }
}
```

Depois execute:
```powershell
python manage.py migrate
python setup.py
```

---

## 🎨 Interface Mobile-First

### Características

✅ **Totalmente Responsivo**
- Mobile: 320px+
- Tablet: 768px+
- Desktop: 1024px+

✅ **Touch-Friendly**
- Botões mínimos de 48x48px
- Gestos suportados
- Swipe navigation

✅ **Performance**
- First Paint < 1s
- Time to Interactive < 2s
- Lighthouse Score 90+

---

## 📊 Estrutura do Projeto

```
web_app/
├── manage.py                 # Django management
├── setup.py                  # Script de configuração
├── requirements.txt          # Dependências
├── README.md                 # Documentação completa
│
├── xml_manager/              # Configuração Django
│   ├── settings.py          # Settings
│   ├── urls.py              # URLs principais
│   └── wsgi.py              # WSGI
│
├── core/                     # App principal
│   ├── models.py            # Models (NFe, CTe, etc)
│   ├── views.py             # Views web
│   ├── urls.py              # URLs core
│   └── admin.py             # Admin
│
├── api/                      # API REST
│   ├── serializers.py       # Serializers
│   ├── views.py             # API views
│   └── urls.py              # API URLs
│
└── templates/                # Templates HTML
    ├── base.html            # Template base
    └── core/                # Templates core
```

---

## 🐛 Troubleshooting

### Erro: "No module named 'django'"

```powershell
pip install -r requirements.txt
```

### Erro: "Port 8000 already in use"

```powershell
# Usar outra porta
python manage.py runserver 8001
```

### Erro: "CSRF token missing"

Na API use Token authentication, não session.

### App mobile não conecta

1. Descubra seu IP local:
```powershell
ipconfig
# Use o IPv4 Address
```

2. No app, use: `http://192.168.x.x:8000/api`

3. Configure CORS em settings.py:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://192.168.x.x:8080",
]
```

---

## 📞 Próximos Passos

### 1. Explorar Interface Web
- ✅ Dashboard com estatísticas
- ✅ Lista de NFes e CTes
- ✅ Análises e relatórios
- ✅ Logs de importação

### 2. Testar API REST
- ✅ Obter token
- ✅ Fazer requisições
- ✅ Testar filtros
- ✅ Verificar paginação

### 3. Desenvolver App Mobile
- ✅ Escolher framework (Flutter/React Native)
- ✅ Implementar autenticação
- ✅ Criar telas principais
- ✅ Integrar com API

### 4. Deploy Produção
- ✅ Configurar Cloud SQL
- ✅ Deploy no Google Cloud
- ✅ Configurar domínio
- ✅ Habilitar HTTPS

---

## 🎉 Sistema Pronto!

Você agora tem:

✅ **Interface Web Responsiva** - Funciona em qualquer dispositivo  
✅ **API REST Completa** - Pronta para app mobile  
✅ **Banco de Dados** - SQLite ou Cloud SQL  
✅ **Autenticação** - Token-based  
✅ **Dashboard** - Estatísticas em tempo real  
✅ **CORS Habilitado** - Para desenvolvimento cross-origin  

---

## 📚 Documentação Completa

- **Sistema Web**: `web_app/README.md`
- **API REST**: http://localhost:8000/api/
- **Admin**: http://localhost:8000/admin/

---

**Bom desenvolvimento! 🚀📱**
