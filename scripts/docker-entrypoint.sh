#!/bin/bash
# Ávila DevOps SaaS - Docker Entrypoint Script
# Script de inicialização para containers de produção

set -e

# Função para log
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

# Verificar variáveis de ambiente obrigatórias
check_env_vars() {
    local required_vars=(
        "SECRET_KEY"
        "DATABASE_URL"
        "REDIS_URL"
    )

    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            log "ERROR: Variável de ambiente obrigatória não definida: $var"
            exit 1
        fi
    done
}

# Aguardar serviços estarem disponíveis
wait_for_services() {
    log "Aguardando serviços..."

    # Aguardar banco de dados
    if [ ! -z "$DATABASE_URL" ]; then
        log "Aguardando banco de dados..."
        python -c "
import os
import time
import psycopg2
from urllib.parse import urlparse

db_url = os.getenv('DATABASE_URL')
if db_url:
    parsed = urlparse(db_url)
    for i in range(30):
        try:
            conn = psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port or 5432,
                user=parsed.username,
                password=parsed.password,
                database=parsed.path.lstrip('/')
            )
            conn.close()
            print('Banco de dados disponível!')
            break
        except:
            print(f'Tentativa {i+1}/30 - Aguardando banco de dados...')
            time.sleep(2)
    else:
        print('ERRO: Banco de dados não disponível após 60 segundos')
        exit(1)
"
    fi

    # Aguardar Redis
    if [ ! -z "$REDIS_URL" ]; then
        log "Aguardando Redis..."
        python -c "
import os
import time
import redis

redis_url = os.getenv('REDIS_URL')
if redis_url:
    for i in range(30):
        try:
            r = redis.from_url(redis_url)
            r.ping()
            print('Redis disponível!')
            break
        except:
            print(f'Tentativa {i+1}/30 - Aguardando Redis...')
            time.sleep(2)
    else:
        print('ERRO: Redis não disponível após 60 segundos')
        exit(1)
"
    fi
}

# Executar migrações se necessário
run_migrations() {
    log "Verificando migrações..."
    python manage.py migrate --check || {
        log "Executando migrações..."
        python manage.py migrate --noinput
    }
}

# Criar superusuário se necessário
create_superuser() {
    if [ "$DJANGO_CREATE_SUPERUSER" = "true" ]; then
        log "Criando superusuário..."
        echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists() or User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')" | python manage.py shell
    fi
}

# Coletar arquivos estáticos se necessário
collect_static() {
    if [ "$COLLECT_STATIC" = "true" ]; then
        log "Coletando arquivos estáticos..."
        python manage.py collectstatic --noinput --clear
    fi
}

# Verificar se é um ambiente de produção
if [ "$ENVIRONMENT" = "production" ]; then
    log "Iniciando aplicação em modo produção..."

    # Verificar variáveis de ambiente
    check_env_vars

    # Aguardar serviços
    wait_for_services

    # Preparar aplicação
    collect_static
    run_migrations
    create_superuser

    # Configurações específicas de produção
    export DJANGO_DEBUG=False
    export SECURE_SSL_REDIRECT=True
    export SECURE_HSTS_SECONDS=31536000

else
    log "Iniciando aplicação em modo desenvolvimento..."

    # Para desenvolvimento, executar migrações sempre
    python manage.py migrate --noinput
fi

# Executar comando passado como argumento
log "Executando comando: $*"
exec "$@"
