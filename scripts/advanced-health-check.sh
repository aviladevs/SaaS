#!/bin/bash
# Ávila DevOps SaaS - Advanced Health Check Script
# Script de monitoramento avançado baseado no feedback

set -e

# Configurações
TIMEOUT=10
RETRIES=3
SERVICES=("landing-page" "recycling-system" "fiscal-system" "clinica-system" "main-app")

# Função para log
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

# Função para testar endpoint de saúde
test_endpoint() {
    local service=$1
    local port=$2
    local path=${3:-/health/}

    for i in $(seq 1 $RETRIES); do
        if curl -f -m $TIMEOUT "http://localhost:$port$path" >/dev/null 2>&1; then
            echo "OK"
            return 0
        fi

        if [ $i -lt $RETRIES ]; then
            sleep 2
        fi
    done

    echo "FAIL"
    return 1
}

# Função para testar conectividade com banco de dados
test_database() {
    python -c "
import os
import sys
import psycopg2
from urllib.parse import urlparse

try:
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        parsed = urlparse(db_url)
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path.lstrip('/'),
            connect_timeout=5
        )
        conn.close()
        print('OK')
    else:
        print('SKIP')
except Exception as e:
    print('FAIL')
    sys.exit(1)
"
}

# Função para testar conectividade com Redis
test_redis() {
    python -c "
import os
import sys
import redis

try:
    redis_url = os.getenv('REDIS_URL')
    if redis_url:
        r = redis.from_url(redis_url, socket_connect_timeout=5)
        r.ping()
        print('OK')
    else:
        print('SKIP')
except Exception as e:
    print('FAIL')
    sys.exit(1)
"
}

# Função para verificar recursos do sistema
check_system_resources() {
    # Memória disponível
    local mem_available=$(cat /proc/meminfo | grep MemAvailable | awk '{print $2}')
    local mem_threshold=$((1024 * 1024))  # 1GB em KB

    if [ $mem_available -lt $mem_threshold ]; then
        echo "FAIL - Memória baixa: ${mem_available}KB"
        return 1
    fi

    # Espaço em disco
    local disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    local disk_threshold=90

    if [ $disk_usage -gt $disk_threshold ]; then
        echo "FAIL - Disco cheio: ${disk_usage}%"
        return 1
    fi

    echo "OK"
}

# Função principal
main() {
    log "🔍 Iniciando health check avançado..."

    local all_ok=true

    # Testar serviços individuais
    for service in "${SERVICES[@]}"; do
        case $service in
            "landing-page")
                result=$(test_endpoint $service 8000 "/")
                ;;
            "clinica-system")
                result=$(test_endpoint $service 3000 "/api/health")
                ;;
            *)
                result=$(test_endpoint $service 8000)
                ;;
        esac

        if [ "$result" = "OK" ]; then
            log "✅ $service: OK"
        else
            log "❌ $service: FAIL"
            all_ok=false
        fi
    done

    # Testar banco de dados
    db_result=$(test_database)
    if [ "$db_result" = "OK" ]; then
        log "✅ Database: OK"
    elif [ "$db_result" = "SKIP" ]; then
        log "⚠️  Database: SKIP (não configurado)"
    else
        log "❌ Database: FAIL"
        all_ok=false
    fi

    # Testar Redis
    redis_result=$(test_redis)
    if [ "$redis_result" = "OK" ]; then
        log "✅ Redis: OK"
    elif [ "$redis_result" = "SKIP" ]; then
        log "⚠️  Redis: SKIP (não configurado)"
    else
        log "❌ Redis: FAIL"
        all_ok=false
    fi

    # Verificar recursos do sistema
    system_result=$(check_system_resources)
    if [ "$system_result" = "OK" ]; then
        log "✅ System Resources: OK"
    else
        log "❌ System Resources: $system_result"
        all_ok=false
    fi

    # Resultado final
    if $all_ok; then
        log "🎉 Todos os checks passaram!"
        exit 0
    else
        log "💥 Alguns checks falharam!"
        exit 1
    fi
}

# Executar se chamado diretamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
