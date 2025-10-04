#!/bin/bash
# Ávila DevOps SaaS - Production Entrypoint Script (Melhorado)
# Script de inicialização otimizado baseado no feedback

set -e

# Função para log com timestamps
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

# Função para sucesso
success() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ✅ $*"
}

# Função para erro
error() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ❌ $*"
}

# Função para warning
warning() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️  $*"
}

# Verificar variáveis de ambiente críticas
check_critical_env_vars() {
    local required_vars=(
        "SECRET_KEY"
        "DATABASE_URL"
        "REDIS_URL"
    )

    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            error "Variável de ambiente crítica não definida: $var"
            exit 1
        fi
    done
}

# Aguardar serviços externos (otimizado)
wait_for_external_services() {
    log "Verificando conectividade com serviços externos..."

    # Aguardar banco de dados PostgreSQL
    if [[ "$DATABASE_URL" =~ postgres ]]; then
        log "Aguardando PostgreSQL..."
        python -c "
import os
import time
import psycopg2
from urllib.parse import urlparse

db_url = os.getenv('DATABASE_URL')
if db_url:
    parsed = urlparse(db_url)
    for i in range(60):  # Timeout aumentado para produção
        try:
            conn = psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port or 5432,
                user=parsed.username,
                password=parsed.password,
                database=parsed.path.lstrip('/'),
                connect_timeout=5
            )
            conn.close()
            print('PostgreSQL conectado!')
            break
        except psycopg2.OperationalError as e:
            if i == 59:
                print(f'ERRO: Não foi possível conectar ao PostgreSQL: {e}')
                exit(1)
            print(f'Tentativa {i+1}/60 - Aguardando PostgreSQL...')
            time.sleep(2)
"
    fi

    # Aguardar Redis
    if [[ ! -z "$REDIS_URL" ]]; then
        log "Aguardando Redis..."
        python -c "
import os
import time
import redis

redis_url = os.getenv('REDIS_URL')
if redis_url:
    for i in range(30):
        try:
            r = redis.from_url(redis_url, socket_connect_timeout=5)
            r.ping()
            print('Redis conectado!')
            break
        except Exception as e:
            if i == 29:
                print(f'ERRO: Não foi possível conectar ao Redis: {e}')
                exit(1)
            print(f'Tentativa {i+1}/30 - Aguardando Redis...')
            time.sleep(2)
"
    fi
}

# Executar migrações de banco de dados
run_database_migrations() {
    log "Verificando migrações do banco de dados..."

    # Verificar se há migrações pendentes
    if ! python manage.py migrate --check >/dev/null 2>&1; then
        log "Executando migrações..."
        python manage.py migrate --noinput
        success "Migrações executadas com sucesso"
    else
        success "Banco de dados já está atualizado"
    fi
}

# Coletar arquivos estáticos (otimizado)
collect_static_files() {
    if [ "$COLLECT_STATIC" = "true" ] || [ "$ENVIRONMENT" = "production" ]; then
        log "Coletando arquivos estáticos..."

        # Coletar apenas se houver mudanças
        if [ ! -d "staticfiles" ] || [ "$(find staticfiles -type f | wc -l)" -eq 0 ]; then
            python manage.py collectstatic --noinput --clear
            success "Arquivos estáticos coletados"
        else
            success "Arquivos estáticos já coletados"
        fi
    fi
}

# Criar superusuário se necessário (apenas em desenvolvimento)
create_superuser_if_needed() {
    if [ "$DJANGO_CREATE_SUPERUSER" = "true" ] && [ "$ENVIRONMENT" != "production" ]; then
        log "Verificando superusuário..."

        if ! python -c "
from django.contrib.auth import get_user_model
User = get_user_model()
print('Superuser exists' if User.objects.filter(is_superuser=True).exists() else 'No superuser')
" | grep -q "Superuser exists"; then

            log "Criando superusuário..."
            echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists() or User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')" | python manage.py shell
            success "Superusuário criado"
        else
            success "Superusuário já existe"
        fi
    fi
}

# Otimizar configurações para produção
optimize_for_production() {
    if [ "$ENVIRONMENT" = "production" ]; then
        log "Aplicando otimizações de produção..."

        # Configurações específicas de produção
        export DJANGO_DEBUG=False
        export SECURE_SSL_REDIRECT=True
        export SECURE_HSTS_SECONDS=31536000
        export SESSION_COOKIE_SECURE=True
        export CSRF_COOKIE_SECURE=True

        # Configurar logging para produção
        export DJANGO_LOG_LEVEL=WARNING

        success "Otimizações de produção aplicadas"
    fi
}

# Verificar saúde da aplicação
health_check() {
    log "Executando health check inicial..."

    # Aguardar um pouco para estabilização
    sleep 5

    if curl -f http://localhost:8000/health/ >/dev/null 2>&1; then
        success "Health check passou"
    else
        error "Health check falhou"
        exit 1
    fi
}

# Função principal
main() {
    log "🚀 Iniciando Ávila DevOps SaaS em modo $ENVIRONMENT..."

    # Verificar ambiente
    if [ "$ENVIRONMENT" = "production" ]; then
        check_critical_env_vars
        wait_for_external_services
        optimize_for_production
    fi

    # Preparar aplicação
    collect_static_files
    run_database_migrations
    create_superuser_if_needed

    # Health check antes de iniciar
    if [ "$SKIP_HEALTH_CHECK" != "true" ]; then
        health_check
    fi

    success "Aplicação preparada com sucesso!"

    # Executar comando passado como argumento
    log "Executando comando: $*"
    exec "$@"
}

# Executar função principal
main "$@"
