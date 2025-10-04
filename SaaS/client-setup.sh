#!/bin/bash
# Ávila DevOps SaaS - One-Click Setup para Clientes
# Script de configuração automática para facilitar a vida dos clientes

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

# Detectar sistema operacional
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# Verificar se usuário tem permissões de administrador
check_admin() {
    if [ "$EUID" -eq 0 ]; then
        error "Não execute este script como root!"
        echo "Execute como usuário normal para maior segurança."
        exit 1
    fi

    success "Executando com usuário normal (recomendado)"
}

# Instalar dependências básicas
install_dependencies() {
    local os=$(detect_os)

    log "Instalando dependências básicas..."

    case $os in
        "linux")
            # Ubuntu/Debian
            if command -v apt &> /dev/null; then
                sudo apt update
                sudo apt install -y curl wget git
            fi
            ;;
        "macos")
            # macOS com Homebrew
            if command -v brew &> /dev/null; then
                brew install curl wget git
            else
                warning "Homebrew não encontrado. Instalando..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
                brew install curl wget git
            fi
            ;;
        "windows")
            # Windows com Chocolatey
            if command -v choco &> /dev/null; then
                choco install curl wget git -y
            else
                warning "Chocolatey não encontrado. Instalando..."
                # Download e instalação manual do Chocolatey seria complexo aqui
                warning "Por favor, instale curl, wget e git manualmente no Windows"
            fi
            ;;
    esac

    success "Dependências instaladas"
}

# Configurar ambiente Python
setup_python() {
    log "Configurando ambiente Python..."

    # Verificar se Python 3.8+ está instalado
    if ! command -v python3 &> /dev/null; then
        error "Python 3 não encontrado. Instalando..."

        local os=$(detect_os)
        case $os in
            "linux")
                sudo apt install -y python3 python3-pip python3-venv
                ;;
            "macos")
                brew install python@3.11
                ;;
        esac
    fi

    # Criar ambiente virtual
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        success "Ambiente virtual criado"
    else
        success "Ambiente virtual já existe"
    fi

    # Ativar ambiente virtual
    source venv/bin/activate

    # Instalar dependências básicas
    pip install --upgrade pip
    pip install requests python-dotenv

    success "Ambiente Python configurado"
}

# Coletar informações do cliente
collect_client_info() {
    echo ""
    echo "🚀 Ávila DevOps SaaS - Configuração Inicial"
    echo "=========================================="
    echo ""

    # Verificar se já foi configurado
    if [ -f ".env" ]; then
        warning "Arquivo .env já existe. Deseja reconfigurar? (s/n)"
        read -r response
        if [[ ! "$response" =~ ^[Ss]$ ]]; then
            echo ""
            echo "✅ Configuração já existe. Pulando etapa inicial."
            return
        fi
    fi

    echo "Por favor, forneça as seguintes informações:"
    echo ""

    read -p "Nome da sua empresa: " COMPANY_NAME
    read -p "Email do administrador: " ADMIN_EMAIL
    read -p "Senha do administrador (mínimo 8 caracteres): " ADMIN_PASSWORD

    if [ ${#ADMIN_PASSWORD} -lt 8 ]; then
        error "Senha deve ter pelo menos 8 caracteres!"
        exit 1
    fi

    # Gerar configurações básicas
    cat > .env << EOF
# Ávila DevOps SaaS - Configuração do Cliente
COMPANY_NAME="$COMPANY_NAME"
ADMIN_EMAIL="$ADMIN_EMAIL"
ADMIN_PASSWORD="$ADMIN_PASSWORD"

# Configurações de produção (serão atualizadas pelo sistema)
ENVIRONMENT=development
DEBUG=True
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")

# URLs da plataforma
LANDING_PAGE_URL=https://aviladevops.com.br
ADMIN_URL=https://admin.aviladevops.com.br

# Configurações locais
DATABASE_URL=sqlite:///db.sqlite3
REDIS_URL=redis://localhost:6379/0
EOF

    success "Arquivo .env criado com sucesso!"
}

# Executar migrações iniciais
run_initial_migrations() {
    log "Executando configurações iniciais..."

    # Ativar ambiente virtual
    source venv/bin/activate

    # Executar script de configuração inicial
    python3 scripts/initial_setup.py

    success "Configurações iniciais concluídas"
}

# Testar conectividade
test_connectivity() {
    log "Testando conectividade com a plataforma..."

    # Testar se consegue acessar a plataforma
    if curl -f -s "https://aviladevops.com.br/health/" > /dev/null; then
        success "Plataforma Ávila DevOps acessível"
    else
        warning "Não foi possível acessar a plataforma principal"
        echo "Isso pode indicar problemas de conectividade ou manutenção programada."
    fi

    # Testar se consegue acessar o admin
    if curl -f -s "https://admin.aviladevops.com.br/health/" > /dev/null; then
        success "Dashboard administrativo acessível"
    else
        warning "Não foi possível acessar o dashboard administrativo"
    fi
}

# Mostrar informações finais
show_completion_info() {
    echo ""
    echo "🎉 CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!"
    echo "======================================"
    echo ""

    if [ -f ".env" ]; then
        source .env
        echo "🏢 Empresa: $COMPANY_NAME"
        echo "📧 Email Admin: $ADMIN_EMAIL"
        echo "🔗 URL da Plataforma: $LANDING_PAGE_URL"
        echo "⚙️  URL do Admin: $ADMIN_URL"
        echo ""
        echo "📋 PRÓXIMOS PASSOS:"
        echo "1. Acesse $ADMIN_URL para fazer login"
        echo "2. Use o email: $ADMIN_EMAIL"
        echo "3. Use a senha configurada durante a instalação"
        echo "4. Complete seu perfil e configurações"
        echo ""
        echo "💡 DICAS:"
        echo "• Mantenha este ambiente atualizado com 'git pull'"
        echo "• Execute 'python manage.py migrate' após atualizações"
        echo "• Monitore os logs com 'tail -f logs/django.log'"
        echo ""
        echo "🛠️  SUPORTE:"
        echo "• Documentação: https://docs.aviladevops.com.br"
        echo "• Email: suporte@aviladevops.com.br"
        echo "• WhatsApp: +55 17 99781-1471"
        echo ""
    fi
}

# Menu principal
show_menu() {
    echo ""
    echo "🚀 Ávila DevOps SaaS - Cliente Setup"
    echo "==================================="
    echo ""
    echo "O que você gostaria de fazer?"
    echo ""
    echo "1) ⚙️  Configuração Inicial Completa"
    echo "2) 🔧 Apenas Instalar Dependências"
    echo "3) 🧪 Testar Conectividade"
    echo "4) 📚 Ver Documentação"
    echo "5) 🛠️  Ferramentas Avançadas"
    echo ""
    echo "0) Sair"
    echo ""
    read -p "Digite sua opção: " choice

    case $choice in
        1) full_setup ;;
        2) install_dependencies ;;
        3) test_connectivity ;;
        4) show_documentation ;;
        5) advanced_tools ;;
        0) exit 0 ;;
        *) error "Opção inválida!"; show_menu ;;
    esac
}

# Configuração completa
full_setup() {
    log "Iniciando configuração completa..."

    check_admin
    install_dependencies
    setup_python
    collect_client_info
    run_initial_migrations
    test_connectivity
    show_completion_info
}

# Apenas instalar dependências
install_dependencies() {
    check_admin
    install_dependencies
    success "Dependências instaladas!"
}

# Testar conectividade
test_connectivity() {
    test_connectivity
    echo ""
    read -p "Pressione Enter para continuar..."
    show_menu
}

# Mostrar documentação
show_documentation() {
    echo ""
    echo "📚 Documentação Ávila DevOps SaaS"
    echo "================================"
    echo ""
    echo "📖 Guias disponíveis:"
    echo "• https://docs.aviladevops.com.br/uso-basico"
    echo "• https://docs.aviladevops.com.br/administracao"
    echo "• https://docs.aviladevops.com.br/integracoes"
    echo ""
    echo "🎥 Vídeos tutoriais:"
    echo "• https://youtube.com/@aviladevops"
    echo ""
    echo "💬 Comunidade:"
    echo "• https://discord.gg/avila-devops"
    echo "• https://github.com/avila-devops/saas/discussions"
    echo ""
    read -p "Pressione Enter para continuar..."
    show_menu
}

# Ferramentas avançadas
advanced_tools() {
    echo ""
    echo "🛠️  Ferramentas Avançadas"
    echo "========================"
    echo ""
    echo "1) 🔄 Atualizar plataforma"
    echo "2) 💾 Fazer backup"
    echo "3) 🔍 Verificar integridade"
    echo "4) 📊 Ver métricas locais"
    echo "5) 🐛 Debug mode"
    echo ""
    read -p "Digite sua opção: " tool_choice

    case $tool_choice in
        1)
            log "Atualizando plataforma..."
            git pull origin main
            source venv/bin/activate
            pip install -r requirements.txt
            python manage.py migrate
            success "Plataforma atualizada!"
            ;;
        2)
            log "Fazendo backup..."
            python scripts/backup_client.py
            success "Backup concluído!"
            ;;
        3)
            log "Verificando integridade..."
            python scripts/integrity_check.py
            success "Verificação concluída!"
            ;;
        4)
            log "Mostrando métricas..."
            python scripts/local_metrics.py
            ;;
        5)
            log "Ativando modo debug..."
            export DEBUG=True
            python manage.py runserver 0.0.0.0:8000
            ;;
        *)
            error "Opção inválida!"
            ;;
    esac

    read -p "Pressione Enter para continuar..."
    show_menu
}

# Função principal
main() {
    # Verificar se está no diretório correto
    if [ ! -f "README.md" ]; then
        error "Execute este script a partir do diretório raiz do projeto"
        exit 1
    fi

    show_menu
}

# Executar
main "$@"
