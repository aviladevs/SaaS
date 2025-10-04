#!/bin/bash

# Deploy Multi-Service SaaS - Ávila DevOps
# Deploy automático de todos os serviços com subdomínios

set -e

echo "🚀 Iniciando deploy completo do SaaS Ávila DevOps..."
echo "================================="

# Configurações
PROJECT_ID="principaldevops"
REGION="us-central1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Função para verificar se o gcloud está configurado
check_gcloud() {
    log_info "Verificando configuração do gcloud..."
    
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI não encontrado. Instale o Google Cloud SDK."
        exit 1
    fi
    
    current_project=$(gcloud config get-value project 2>/dev/null)
    if [ "$current_project" != "$PROJECT_ID" ]; then
        log_warning "Configurando projeto: $PROJECT_ID"
        gcloud config set project $PROJECT_ID
    fi
    
    log_success "gcloud configurado corretamente"
}

# Função para fazer deploy de um serviço específico
deploy_service() {
    local service_name=$1
    local service_path=$2
    local app_yaml_path=$3
    
    log_info "Deploying $service_name..."
    
    if [ ! -f "$app_yaml_path" ]; then
        log_error "app.yaml não encontrado em: $app_yaml_path"
        return 1
    fi
    
    cd "$service_path"
    
    # Verificar se há requirements.txt ou package.json
    if [ -f "requirements.txt" ]; then
        log_info "Projeto Python detectado para $service_name"
    elif [ -f "package.json" ]; then
        log_info "Projeto Node.js detectado para $service_name"
    fi
    
    # Deploy
    log_info "Executando deploy do $service_name..."
    if gcloud app deploy "$app_yaml_path" --quiet --version="v$(date +%Y%m%d%H%M)"; then
        log_success "$service_name deployado com sucesso!"
    else
        log_error "Falha no deploy do $service_name"
        return 1
    fi
    
    cd - > /dev/null
}

# Função principal de deploy
main_deploy() {
    local base_dir="$(pwd)"
    
    # 1. Deploy do serviço principal (default)
    log_info "=== Deploy do App Principal (default) ==="
    deploy_service "App Principal" "$base_dir/app-aviladevops" "$base_dir/app-aviladevops/app.yaml"
    
    # 2. Deploy da Landing Page
    log_info "=== Deploy da Landing Page ==="
    deploy_service "Landing Page" "$base_dir/LANDING-PAGE" "$base_dir/LANDING-PAGE/app.yaml"
    
    # 3. Deploy do Sistema de Gestão
    log_info "=== Deploy do Sistema de Gestão ==="
    deploy_service "Sistema" "$base_dir/sistema" "$base_dir/sistema/app.yaml"
    
    # 4. Deploy do Sistema Fiscal
    log_info "=== Deploy do Sistema Fiscal ==="
    deploy_service "Fiscal" "$base_dir/fiscal/web_app" "$base_dir/fiscal/web_app/app.yaml"
    
    # 5. Deploy da Clínica (Next.js)
    log_info "=== Deploy da Clínica (Next.js) ==="
    deploy_service "Clínica" "$base_dir/clinica" "$base_dir/clinica/app.yaml"
    
    # 6. Deploy do dispatch.yaml (roteamento de subdomínios)
    log_info "=== Configurando roteamento de subdomínios ==="
    if [ -f "$base_dir/dispatch.yaml" ]; then
        log_info "Deployando dispatch.yaml..."
        gcloud app deploy "$base_dir/dispatch.yaml" --quiet
        log_success "Roteamento de subdomínios configurado!"
    else
        log_warning "dispatch.yaml não encontrado"
    fi
}

# Função para verificar status dos serviços
check_services_status() {
    log_info "=== Verificando status dos serviços ==="
    
    echo "Listando versões deployadas:"
    gcloud app versions list
    
    echo ""
    echo "Serviços disponíveis:"
    gcloud app services list
    
    echo ""
    echo "URLs dos serviços:"
    echo "🏠 Landing Page: https://aviladevops.com.br"
    echo "🚀 App Principal: https://app.aviladevops.com.br"
    echo "⚙️  Sistema: https://sistema.aviladevops.com.br"
    echo "📊 Fiscal: https://fiscal.aviladevops.com.br"
    echo "🏥 Clínica: https://clinica.aviladevops.com.br"
}

# Função para limpeza de versões antigas
cleanup_old_versions() {
    log_info "=== Limpeza de versões antigas ==="
    
    # Manter apenas as 3 versões mais recentes de cada serviço
    services=("default" "landing" "sistema" "fiscal" "clinica")
    
    for service in "${services[@]}"; do
        log_info "Limpando versões antigas do serviço: $service"
        
        # Listar versões e manter apenas as 3 mais recentes
        versions=$(gcloud app versions list --service="$service" --sort-by="~version.createTime" --format="value(version.id)" | tail -n +4)
        
        if [ ! -z "$versions" ]; then
            echo "$versions" | while IFS= read -r version; do
                if [ ! -z "$version" ]; then
                    log_warning "Deletando versão antiga: $service/$version"
                    gcloud app versions delete "$version" --service="$service" --quiet || true
                fi
            done
        fi
    done
    
    log_success "Limpeza concluída!"
}

# Menu principal
show_menu() {
    echo ""
    echo "🚀 Deploy Multi-Service SaaS - Ávila DevOps"
    echo "============================================"
    echo "1. Deploy completo (todos os serviços)"
    echo "2. Deploy apenas App Principal"
    echo "3. Deploy apenas Landing Page"
    echo "4. Deploy apenas Sistema"
    echo "5. Deploy apenas Fiscal"
    echo "6. Deploy apenas Clínica"
    echo "7. Configurar apenas dispatch.yaml"
    echo "8. Verificar status dos serviços"
    echo "9. Limpeza de versões antigas"
    echo "0. Sair"
    echo ""
    read -p "Escolha uma opção: " choice
}

# Execução baseada no menu
case "${1:-menu}" in
    "all"|"completo")
        check_gcloud
        main_deploy
        check_services_status
        log_success "Deploy completo finalizado!"
        ;;
    "app")
        check_gcloud
        deploy_service "App Principal" "$(pwd)/app-aviladevops" "$(pwd)/app-aviladevops/app.yaml"
        ;;
    "landing")
        check_gcloud
        deploy_service "Landing Page" "$(pwd)/LANDING-PAGE" "$(pwd)/LANDING-PAGE/app.yaml"
        ;;
    "sistema")
        check_gcloud
        deploy_service "Sistema" "$(pwd)/sistema" "$(pwd)/sistema/app.yaml"
        ;;
    "fiscal")
        check_gcloud
        deploy_service "Fiscal" "$(pwd)/fiscal/web_app" "$(pwd)/fiscal/web_app/app.yaml"
        ;;
    "clinica")
        check_gcloud
        deploy_service "Clínica" "$(pwd)/clinica" "$(pwd)/clinica/app.yaml"
        ;;
    "dispatch")
        check_gcloud
        gcloud app deploy "$(pwd)/dispatch.yaml" --quiet
        ;;
    "status")
        check_gcloud
        check_services_status
        ;;
    "cleanup")
        check_gcloud
        cleanup_old_versions
        ;;
    "menu")
        while true; do
            show_menu
            case $choice in
                1) 
                    check_gcloud
                    main_deploy
                    check_services_status
                    ;;
                2) 
                    check_gcloud
                    deploy_service "App Principal" "$(pwd)/app-aviladevops" "$(pwd)/app-aviladevops/app.yaml"
                    ;;
                3) 
                    check_gcloud
                    deploy_service "Landing Page" "$(pwd)/LANDING-PAGE" "$(pwd)/LANDING-PAGE/app.yaml"
                    ;;
                4) 
                    check_gcloud
                    deploy_service "Sistema" "$(pwd)/sistema" "$(pwd)/sistema/app.yaml"
                    ;;
                5) 
                    check_gcloud
                    deploy_service "Fiscal" "$(pwd)/fiscal/web_app" "$(pwd)/fiscal/web_app/app.yaml"
                    ;;
                6) 
                    check_gcloud
                    deploy_service "Clínica" "$(pwd)/clinica" "$(pwd)/clinica/app.yaml"
                    ;;
                7) 
                    check_gcloud
                    gcloud app deploy "$(pwd)/dispatch.yaml" --quiet
                    ;;
                8) 
                    check_gcloud
                    check_services_status
                    ;;
                9) 
                    check_gcloud
                    cleanup_old_versions
                    ;;
                0) 
                    log_info "Saindo..."
                    exit 0
                    ;;
                *) 
                    log_error "Opção inválida!"
                    ;;
            esac
            echo ""
            read -p "Pressione Enter para continuar..."
        done
        ;;
    *)
        echo "Uso: $0 [all|app|landing|sistema|fiscal|clinica|dispatch|status|cleanup|menu]"
        echo ""
        echo "Exemplos:"
        echo "  $0 all       # Deploy completo"
        echo "  $0 app       # Deploy apenas do app principal"
        echo "  $0 status    # Verificar status"
        echo "  $0           # Menu interativo"
        exit 1
        ;;
esac