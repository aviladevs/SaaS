"""
Django settings for PRODUCTION deployment on Google Cloud Platform
"""

import os
from .settings import *

# SECURITY
DEBUG = False
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', SECRET_KEY)

# Allowed hosts - adicione seu domínio
ALLOWED_HOSTS = [
    '.appspot.com',
    'fiscal.aviladevops.com.br',
    'www.fiscal.aviladevops.com.br',
]

# HTTPS/Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Database - Cloud SQL
# Se quiser usar Cloud SQL, descomente e configure:
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'xml_fiscais'),
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', '/cloudsql/PROJECT_ID:REGION:INSTANCE'),
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        }
    }
}
"""

# Static files
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# CORS - Em produção, especifique os domínios permitidos
CORS_ALLOWED_ORIGINS = [
    "https://fiscal.aviladevops.com.br",
    "https://www.fiscal.aviladevops.com.br",
    "capacitor://localhost",
    "ionic://localhost",
]

# Session timeout
SESSION_COOKIE_AGE = 86400  # 24 horas
