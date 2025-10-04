#!/bin/bash
# Ávila DevOps SaaS - Docker Management Script
# Script para facilitar o gerenciamento do ambiente Docker

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $*${NC}"
}

# Função para sucesso
success() {
    echo -e "${GREEN}✅ $*${NC}"
}

# Função para erro
error() {
    echo -e "${RED}❌ $*${NC}"
}

# Função para warning
warning() {
    echo -e "${YELLOW}⚠️  $*${NC}"
}

# Verificar se Docker está instalado
check_docker() {
    if ! command -v docker &> /dev/null; then
        error "Docker não está instalado. Instale o Docker primeiro."
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose não está instalado. Instale o Docker Compose primeiro."
        exit 1
    fi
}

# Função para verificar se arquivo .env existe
check_env() {
    if [ ! -f .env ]; then
        warning "Arquivo .env não encontrado. Copiando .env.example..."
        cp .env.example .env
        warning "Por favor, edite o arquivo .env com suas configurações antes de continuar."
        exit 1
    fi
}

# Iniciar ambiente de desenvolvimento
dev() {
    log "🚀 Iniciando ambiente de desenvolvimento..."
    check_env

    docker-compose -f docker-compose.dev.yml up -d

    log "Aguardando serviços iniciarem..."
    sleep 10

    success "Ambiente iniciado!"
    echo ""
    echo "🌐 URLs disponíveis:"
    echo "   Landing Page: http://localhost:8000"
    echo "   Sistema:      http://localhost:8001"
    echo "   Fiscal:       http://localhost:8002"
    echo "   Clínica:      http://localhost:3000"
    echo "   Admin:        http://localhost:8003"
    echo ""
    echo "📊 Para ver logs: make logs"
    echo "🛑 Para parar: make stop"
}

# Iniciar ambiente de produção
prod() {
    log "🏭 Iniciando ambiente de produção..."
    check_env

    docker-compose -f docker-compose.prod.yml up -d

    log "Aguardando serviços iniciarem..."
    sleep 15

    success "Ambiente de produção iniciado!"
    echo ""
    echo "🌐 URLs disponíveis:"
    echo "   Landing Page: http://localhost"
    echo "   Sistema:      http://localhost/sistema/"
    echo "   Fiscal:       http://localhost/fiscal/"
    echo "   Clínica:      http://localhost/clinica/"
    echo "   Admin:        http://localhost/admin/"
    echo ""
    echo "📊 Para ver logs: make logs"
    echo "🛑 Para parar: make stop"
}

# Parar todos os serviços
stop() {
    log "⏹️  Parando todos os serviços..."

    docker-compose -f docker-compose.dev.yml down 2>/dev/null || true
    docker-compose -f docker-compose.prod.yml down 2>/dev/null || true

    success "Todos os serviços parados!"
}

# Ver logs
logs() {
    echo "📋 Mostrando logs dos serviços..."
    echo ""
    docker-compose -f docker-compose.dev.yml logs -f
}

# Build das imagens
build() {
    log "🏗️  Buildando imagens Docker..."

    # Build desenvolvimento
    docker-compose -f docker-compose.dev.yml build

    # Build produção
    docker-compose -f docker-compose.prod.yml build

    success "Todas as imagens buildadas!"
}

# Executar testes
test() {
    log "🧪 Executando testes..."

    # Testes para cada serviço
    for service in landing-page recycling-system fiscal-system main-app; do
        if [ -d "$service" ]; then
            log "Testando $service..."
            docker-compose -f docker-compose.dev.yml exec $service python manage.py test --verbosity=1 || warning "Testes falharam para $service"
        fi
    done

    success "Testes concluídos!"
}

# Limpar ambiente
clean() {
    log "🧹 Limpando ambiente Docker..."

    stop

    # Remover volumes
    docker volume prune -f

    # Remover imagens não utilizadas
    docker image prune -f

    # Limpar containers parados
    docker container prune -f

    success "Ambiente limpo!"
}

# Backup do banco de dados
backup() {
    log "💾 Criando backup do banco de dados..."

    BACKUP_DIR="./backups"
    mkdir -p "$BACKUP_DIR"

    BACKUP_FILE="$BACKUP_DIR/db-backup-$(date +%Y%m%d-%H%M%S).sql"

    docker-compose -f docker-compose.dev.yml exec -T db pg_dump \
        -h localhost \
        -U postgres \
        -d aviladevops_saas_dev \
        > "$BACKUP_FILE"

    success "Backup criado: $BACKUP_FILE"
}

# Health check dos serviços
health() {
    log "🏥 Verificando saúde dos serviços..."

    services=("landing-page:8000" "recycling-system:8001" "fiscal-system:8002" "clinica-system:3000" "main-app:8003")

    for service in "${services[@]}"; do
        service_name=$(echo $service | cut -d: -f1)
        port=$(echo $service | cut -d: -f2)

        if curl -f "http://localhost:$port/health/" &>/dev/null; then
            success "$service_name: OK"
        else
            error "$service_name: FALHOU"
        fi
    done
}

# Mostrar status dos serviços
status() {
    log "📊 Status dos serviços:"

    echo ""
    docker-compose -f docker-compose.dev.yml ps
    echo ""
    docker-compose -f docker-compose.prod.yml ps
}

# Instalar dependências
install() {
    log "📦 Instalando dependências..."

    # Instalar Python dependencies
    for service in landing-page sistema fiscal app-aviladevops; do
        if [ -d "$service" ] && [ -f "$service/requirements.txt" ]; then
            log "Instalando dependências para $service..."
            pip install -r "$service/requirements.txt"
        fi
    done

    # Instalar Node.js dependencies
    if [ -d "clinica" ] && [ -f "clinica/package.json" ]; then
        log "Instalando dependências Node.js para clinica..."
        cd clinica && npm install
        cd ..
    fi

    success "Dependências instaladas!"
}

# Executar migrações
migrate() {
    log "🗄️  Executando migrações..."

    for service in main-app recycling-system fiscal-system; do
        if [ -d "$service" ]; then
            log "Executando migrações para $service..."
            docker-compose -f docker-compose.dev.yml exec $service python manage.py migrate
        fi
    done

    success "Migrações executadas!"
}

# Criar superusuário
superuser() {
    log "👑 Criando superusuário..."

    docker-compose -f docker-compose.dev.yml exec main-app python manage.py createsuperuser --noinput || \
    docker-compose -f docker-compose.dev.yml exec main-app python manage.py createsuperuser

    success "Superusuário criado!"
}

# Ajuda
help() {
    echo "🚀 Ávila DevOps SaaS - Docker Management"
    echo ""
    echo "Comandos disponíveis:"
    echo ""
    echo "💻 Desenvolvimento:"
    echo "  $0 dev          - Inicia ambiente de desenvolvimento"
    echo "  $0 prod         - Inicia ambiente de produção"
    echo "  $0 install      - Instala dependências"
    echo "  $0 build        - Builda imagens Docker"
    echo "  $0 test         - Executa testes"
    echo ""
    echo "🔧 Operações:"
    echo "  $0 migrate      - Executa migrações do banco"
    echo "  $0 superuser    - Cria superusuário"
    echo "  $0 backup       - Cria backup do banco"
    echo "  $0 health       - Verifica saúde dos serviços"
    echo "  $0 logs         - Mostra logs dos serviços"
    echo "  $0 status       - Mostra status dos serviços"
    echo ""
    echo "🧹 Manutenção:"
    echo "  $0 stop         - Para todos os serviços"
    echo "  $0 clean        - Limpa ambiente Docker"
    echo ""
    echo "📋 Ajuda:"
    echo "  $0 help         - Mostra esta ajuda"
}

# Main script
main() {
    check_docker

    case "${1:-help}" in
        dev) dev ;;
        prod) prod ;;
        install) install ;;
        build) build ;;
        test) test ;;
        migrate) migrate ;;
        superuser) superuser ;;
        backup) backup ;;
        health) health ;;
        logs) logs ;;
        status) status ;;
        stop) stop ;;
        clean) clean ;;
        help|*) help ;;
    esac
}

main "$@"
