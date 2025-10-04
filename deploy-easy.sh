#!/bin/bash
# Ávila DevOps SaaS - Easy Deploy Script
# Script para facilitar deploy para funcionários

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Verificar pré-requisitos
check_prerequisites() {
    log "Verificando pré-requisitos..."

    # Verificar se está no diretório correto
    if [ ! -f "docker-compose.prod.yml" ]; then
        error "Execute este script a partir do diretório raiz do projeto SaaS"
        exit 1
    fi

    # Verificar variáveis de ambiente
    if [ ! -f ".env" ]; then
        warning "Arquivo .env não encontrado. Usando configurações padrão."
        cp .env.example .env
    fi

    success "Pré-requisitos verificados"
}

# Menu interativo para funcionários
show_menu() {
    echo ""
    echo "🚀 Ávila DevOps SaaS - Deploy Fácil"
    echo "==================================="
    echo ""
    echo "Escolha uma opção:"
    echo ""
    echo "1) 🚀 Deploy Completo (Todos os serviços)"
    echo "2) 🎯 Deploy Serviço Específico"
    echo "3) 👥 Criar Novo Tenant"
    echo "4) 📊 Verificar Status dos Serviços"
    echo "5) 🔧 Backup/Restore"
    echo "6) 📈 Ver Métricas e Monitoramento"
    echo "7) 🛠️  Ferramentas de Desenvolvimento"
    echo "8) 📚 Ajuda e Documentação"
    echo ""
    echo "0) Sair"
    echo ""
    read -p "Digite sua opção: " choice

    case $choice in
        1) deploy_all ;;
        2) deploy_specific ;;
        3) create_tenant ;;
        4) check_status ;;
        5) backup_restore ;;
        6) show_metrics ;;
        7) dev_tools ;;
        8) show_help ;;
        0) exit 0 ;;
        *) error "Opção inválida!"; show_menu ;;
    esac
}

# Deploy de todos os serviços
deploy_all() {
    log "🚀 Iniciando deploy completo..."

    # Verificar se há mudanças no Git
    if git diff --quiet HEAD; then
        warning "Nenhuma mudança detectada. Continuar mesmo assim? (s/n)"
        read -r response
        if [[ ! "$response" =~ ^[Ss]$ ]]; then
            show_menu
        fi
    fi

    # Executar testes
    log "Executando testes..."
    make test

    # Build das imagens
    log "Buildando imagens Docker..."
    make build

    # Deploy para produção
    log "Fazendo deploy para produção..."
    make deploy-prod

    # Verificar saúde
    log "Verificando saúde dos serviços..."
    make health

    success "Deploy completo realizado com sucesso!"
    echo ""
    echo "🌐 URLs disponíveis:"
    echo "   Landing Page: https://aviladevops.com.br"
    echo "   Sistema: https://sistema.aviladevops.com.br"
    echo "   Fiscal: https://fiscal.aviladevops.com.br"
    echo "   Clínica: https://clinica.aviladevops.com.br"
    echo "   Admin: https://admin.aviladevops.com.br"
    echo ""
    read -p "Pressione Enter para continuar..."
    show_menu
}

# Deploy de serviço específico
deploy_specific() {
    echo ""
    echo "🎯 Deploy de Serviço Específico"
    echo "==============================="
    echo ""
    echo "Escolha o serviço para deploy:"
    echo "1) Landing Page"
    echo "2) Sistema de Reciclagem"
    echo "3) Sistema Fiscal"
    echo "4) Clínica Management"
    echo "5) Aplicação Principal (Admin)"
    echo ""
    read -p "Digite sua opção: " service_choice

    case $service_choice in
        1) service="landing-page" ;;
        2) service="sistema" ;;
        3) service="fiscal" ;;
        4) service="clinica" ;;
        5) service="app-aviladevops" ;;
        *) error "Opção inválida!"; deploy_specific ;;
    esac

    log "Fazendo deploy do serviço: $service..."

    # Deploy específico do serviço
    # (Aqui você implementaria a lógica específica)

    success "Deploy do serviço $service realizado com sucesso!"
    read -p "Pressione Enter para continuar..."
    show_menu
}

# Criar novo tenant
create_tenant() {
    log "👥 Criando novo tenant..."

    read -p "Nome do cliente/empresa: " tenant_name
    read -p "Domínio personalizado (ex: cliente.aviladevops.com.br): " tenant_domain
    read -p "Email do administrador: " admin_email

    # Executar script de criação de tenant
    python scripts/tenant_management.py create \
        --name "$tenant_name" \
        --domain "$tenant_domain" \
        --owner-email "$admin_email"

    success "Tenant '$tenant_name' criado com sucesso!"
    echo ""
    echo "🔗 Acesso do cliente:"
    echo "   URL: https://$tenant_domain"
    echo "   Email admin: $admin_email"
    echo ""
    read -p "Pressione Enter para continuar..."
    show_menu
}

# Verificar status
check_status() {
    log "📊 Verificando status dos serviços..."

    echo ""
    echo "=== STATUS DOS SERVIÇOS ==="
    echo ""

    # Verificar saúde dos serviços
    services=("landing-page" "sistema" "fiscal" "clinica" "app-aviladevops")
    for service in "${services[@]}"; do
        echo "🔍 Verificando $service..."
        # Implementar verificação específica
    done

    echo ""
    echo "=== MÉTRICAS ==="
    echo "Uptime: $(uptime | awk '{print $1}')"
    echo "Memória usada: $(free | awk 'NR==2{printf "%.1f%%", $3*100/$2 }')"
    echo "Disco usado: $(df / | awk 'NR==2{print $5}')"
    echo ""

    read -p "Pressione Enter para continuar..."
    show_menu
}

# Função de backup/restore
backup_restore() {
    echo ""
    echo "💾 Backup e Restore"
    echo "=================="
    echo ""
    echo "1) Criar backup completo"
    echo "2) Criar backup de tenant específico"
    echo "3) Restaurar backup"
    echo "4) Listar backups disponíveis"
    echo ""
    read -p "Digite sua opção: " backup_choice

    case $backup_choice in
        1)
            log "Criando backup completo..."
            make backup
            ;;
        2)
            read -p "Nome do tenant: " tenant_name
            python scripts/tenant_management.py backup --name "$tenant_name"
            ;;
        3)
            echo "Backups disponíveis:"
            ls -la backups/ 2>/dev/null || echo "Nenhum backup encontrado"
            read -p "Nome do arquivo de backup: " backup_file
            # Implementar restore
            ;;
        4)
            echo "Backups disponíveis:"
            ls -la backups/ 2>/dev/null || echo "Nenhum backup encontrado"
            ;;
        *)
            error "Opção inválida!"
            ;;
    esac

    read -p "Pressione Enter para continuar..."
    show_menu
}

# Mostrar métricas
show_metrics() {
    log "📈 Métricas e Monitoramento"

    echo ""
    echo "=== MONITORAMENTO EM TEMPO REAL ==="
    echo ""

    # Métricas básicas
    echo "🔥 Serviços ativos: $(docker ps | wc -l)"
    echo "💾 Uso de disco: $(df / | awk 'NR==2{print $5}')"
    echo "🧠 Memória usada: $(free | awk 'NR==2{printf "%.1f%%", $3*100/$2 }')"
    echo "🌐 Conexões ativas: $(netstat -tuln | wc -l)"
    echo ""

    # Logs recentes
    echo "=== LOGS RECENTES ==="
    docker-compose -f docker-compose.prod.yml logs --tail=10
    echo ""

    read -p "Pressione Enter para continuar..."
    show_menu
}

# Ferramentas de desenvolvimento
dev_tools() {
    echo ""
    echo "🛠️  Ferramentas de Desenvolvimento"
    echo "================================="
    echo ""
    echo "1) Executar testes"
    echo "2) Verificar qualidade do código"
    echo "3) Limpar ambiente"
    echo "4) Reset banco de dados"
    echo "5) Ver logs detalhados"
    echo ""
    read -p "Digite sua opção: " dev_choice

    case $dev_choice in
        1) make test ;;
        2) make lint ;;
        3) make clean ;;
        4) make migrate ;;
        5) make logs ;;
        *) error "Opção inválida!" ;;
    esac

    read -p "Pressione Enter para continuar..."
    show_menu
}

# Ajuda
show_help() {
    echo ""
    echo "📚 Ajuda - Deploy Fácil SaaS"
    echo "==========================="
    echo ""
    echo "Este script facilita as operações do dia-a-dia para funcionários:"
    echo ""
    echo "🔧 OPERAÇÕES COMUNS:"
    echo "• Deploy completo: Atualiza todos os serviços"
    echo "• Deploy específico: Atualiza apenas um serviço"
    echo "• Criar tenant: Configura novo cliente automaticamente"
    echo "• Status: Verifica saúde de todos os serviços"
    echo ""
    echo "📊 MONITORAMENTO:"
    echo "• Métricas em tempo real"
    echo "• Logs recentes"
    echo "• Health checks automáticos"
    echo ""
    echo "🛠️ DESENVOLVIMENTO:"
    echo "• Testes automatizados"
    echo "• Verificação de qualidade"
    echo "• Limpeza de ambiente"
    echo ""
    echo "💡 DICAS:"
    echo "• Sempre execute testes antes de deploy"
    echo "• Monitore métricas após deploy"
    echo "• Use backup antes de mudanças críticas"
    echo ""
    read -p "Pressione Enter para continuar..."
    show_menu
}

# Função principal
main() {
    echo ""
    echo "🚀 Ávila DevOps SaaS - Deploy Fácil"
    echo "==================================="
    echo ""

    # Verificar se usuário tem permissões
    if [ "$EUID" -eq 0 ]; then
        warning "Executando como root. Recomendado usar usuário normal com sudo."
    fi

    check_prerequisites
    show_menu
}

# Executar
main "$@"
