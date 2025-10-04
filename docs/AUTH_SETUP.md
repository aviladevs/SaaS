# Multi-Tenant Authentication System - Setup Guide

## Prerequisites

- Python 3.8+
- PostgreSQL 12+ (recommended for production)
- Redis 6+ (for session management and caching)
- Node.js 16+ (for frontend development)

## Installation

### 1. Install Python Dependencies

```bash
cd app-aviladevops
pip install -r requirements.txt
```

Required packages:
- Django 4.2+
- djangorestframework
- djangorestframework-simplejwt
- django-allauth
- dj-rest-auth
- django-cors-headers
- django-filter
- django-redis
- pyotp
- qrcode
- python-dotenv

### 2. Environment Configuration

Create a `.env` file in the `app-aviladevops` directory:

```env
# Django Settings
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,*.aviladevops.com.br

# Database (PostgreSQL for production)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=aviladevops
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

# Redis (for caching and sessions)
REDIS_URL=redis://localhost:6379/1

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@aviladevops.com.br

# OAuth Providers (Optional - configure per tenant via admin)
# These are fallback defaults if not configured per tenant
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret

GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# Security Settings (Production)
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
```

### 3. Database Setup

#### Development (SQLite)
```bash
python manage.py makemigrations
python manage.py migrate
```

#### Production (PostgreSQL)
```bash
# Create database
createdb aviladevops

# Run migrations
python manage.py migrate
```

### 4. Create Superuser

```bash
python manage.py createsuperuser
```

### 5. Create Initial Tenant

```bash
python manage.py shell
```

```python
from apps.users.models import Tenant, Role, Permission
from django.contrib.auth import get_user_model

User = get_user_model()

# Create tenant
tenant = Tenant.objects.create(
    name="My Company",
    slug="my-company",
    domain="my-company.aviladevops.com.br",
    owner_email="owner@mycompany.com",
    plan="pro",
    max_users=100,
    storage_limit=100,
    status="active"
)

# Create default roles
admin_role = Role.objects.create(
    tenant=tenant,
    name="Admin",
    description="Full access to all features",
    is_system=True
)

user_role = Role.objects.create(
    tenant=tenant,
    name="User",
    description="Standard user access",
    is_system=True
)

# Create permissions for admin role
resources = ['user', 'tenant', 'service', 'project', 'blog', 'contact', 'analytics', 'settings']
actions = ['create', 'read', 'update', 'delete', 'list', 'export']

for resource in resources:
    for action in actions:
        Permission.objects.create(
            role=admin_role,
            resource=resource,
            action=action
        )

# Create tenant owner user
owner = User.objects.create_user(
    username='owner',
    email='owner@mycompany.com',
    password='ChangeMe123!',
    tenant=tenant,
    first_name='Owner',
    last_name='User',
    is_verified=True
)
owner.roles.add(admin_role)

print(f"Tenant created: {tenant}")
print(f"Owner created: {owner}")
```

### 6. Configure OAuth Providers (Optional)

#### Google Workspace

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials:
   - Application type: Web application
   - Authorized redirect URIs: `https://your-domain.com/api/auth/google/callback/`
5. Add credentials to tenant via admin or API

#### Microsoft Azure AD

1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to Azure Active Directory > App registrations
3. Create new registration:
   - Redirect URI: `https://your-domain.com/api/auth/microsoft/callback/`
4. Note the Application (client) ID
5. Create a client secret under Certificates & secrets
6. Add credentials to tenant

#### SAML 2.0

1. Obtain SAML metadata URL from your identity provider
2. Configure via admin panel or API
3. Provide your SP metadata to the IdP:
   - Entity ID: `https://your-domain.com/api/auth/saml/metadata/`
   - ACS URL: `https://your-domain.com/api/auth/saml/acs/`

### 7. Run Development Server

```bash
python manage.py runserver
```

Access the application:
- API: http://localhost:8000/api/
- Admin: http://localhost:8000/admin/
- Auth API: http://localhost:8000/api/auth/

### 8. Test Authentication

```bash
# Get JWT token
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "owner", "password": "ChangeMe123!"}'

# Use token
curl -X GET http://localhost:8000/api/auth/users/ \
  -H "Authorization: Bearer <your-token>"
```

## Production Deployment

### 1. Database

Use PostgreSQL with connection pooling:

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'aviladevops',
        'USER': 'postgres',
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}
```

### 2. Redis for Sessions and Caching

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            }
        },
        'KEY_PREFIX': 'aviladevops',
        'TIMEOUT': 300,
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

### 3. Static Files

```bash
python manage.py collectstatic --noinput
```

### 4. WSGI/ASGI Server

Use Gunicorn with multiple workers:

```bash
gunicorn core.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
```

### 5. Nginx Configuration

```nginx
upstream django {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name *.aviladevops.com.br;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name *.aviladevops.com.br;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    client_max_body_size 20M;

    location /static/ {
        alias /path/to/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias /path/to/media/;
        expires 30d;
    }

    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 6. SSL/TLS

Use Let's Encrypt:

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d *.aviladevops.com.br
```

### 7. Monitoring

Configure error tracking with Sentry:

```python
# settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True
)
```

## Multi-Tenant Setup

### Subdomain Configuration

Each tenant gets their own subdomain:
- `company-a.aviladevops.com.br`
- `company-b.aviladevops.com.br`

The `TenantMiddleware` automatically detects the tenant from the subdomain.

### DNS Configuration

Add wildcard DNS record:
```
*.aviladevops.com.br  A  your-server-ip
```

### Tenant Isolation

Data is automatically isolated by tenant:
- Users can only see data from their tenant
- API endpoints filter by tenant automatically
- Permissions are checked per tenant

## Security Checklist

- [ ] Change SECRET_KEY in production
- [ ] Enable HTTPS and SSL redirects
- [ ] Configure CORS for your domains
- [ ] Enable Django security middleware
- [ ] Set up database backups
- [ ] Configure Redis password
- [ ] Enable rate limiting
- [ ] Set up monitoring and alerts
- [ ] Regular security updates
- [ ] Enable MFA for admin accounts
- [ ] Review and rotate OAuth secrets
- [ ] Configure firewall rules
- [ ] Set up audit log monitoring
- [ ] Implement backup and disaster recovery

## Troubleshooting

### Token expires too quickly
Adjust JWT settings in `settings.py`:
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}
```

### OAuth callback errors
Check redirect URIs match exactly in provider settings

### Tenant not detected
Ensure subdomain is correctly configured in DNS and Tenant model

### Permission denied errors
Verify user has correct roles and permissions assigned

### MFA not working
Check system time synchronization (TOTP requires accurate time)

## Support

For issues or questions:
- GitHub Issues: https://github.com/aviladevs/SaaS/issues
- Email: support@aviladevops.com.br
