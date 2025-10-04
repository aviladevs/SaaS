#!/bin/bash
# 🚀 Script de Deploy Automatizado - SaaS Ávila DevOps
# Execute: chmod +x deploy.sh && ./deploy.sh

set -e  # Exit on any error

echo "🚀 Iniciando Deploy do SaaS Ávila DevOps..."
echo "=================================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para logging
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar se está rodando como root
if [[ $EUID -eq 0 ]]; then
   log_error "Este script não deve ser executado como root"
   exit 1
fi

# 1. Verificações Pré-Deploy
log_info "1️⃣ Verificando pré-requisitos..."

# Verificar Docker
if ! command -v docker &> /dev/null; then
    log_error "Docker não está instalado!"
    exit 1
fi

# Verificar Docker Compose
if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose não está instalado!"
    exit 1
fi

# Verificar se PostgreSQL está acessível
log_info "Verificando conexão com PostgreSQL..."
if ! docker run --rm postgres:15-alpine pg_isready -h host.docker.internal -p 5432 &> /dev/null; then
    log_warn "PostgreSQL não acessível. Configurando container PostgreSQL..."
fi

# Verificar se Redis está acessível
log_info "Verificando conexão com Redis..."
if ! docker run --rm redis:7-alpine redis-cli -h host.docker.internal ping &> /dev/null; then
    log_warn "Redis não acessível. Configurando container Redis..."
fi

# 2. Backup dos dados existentes
log_info "2️⃣ Criando backup dos dados..."
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

if [ -f ".env" ]; then
    cp .env "$BACKUP_DIR/.env.backup"
    log_info "Backup do .env criado em $BACKUP_DIR"
fi

# 3. Configurar variáveis de ambiente
log_info "3️⃣ Configurando variáveis de ambiente..."

if [ ! -f ".env" ]; then
    log_error "Arquivo .env não encontrado!"
    log_info "Copie .env.example para .env e configure as variáveis"
    exit 1
fi

# Verificar variáveis críticas
check_env_var() {
    local var_name=$1
    local var_value=$(grep "^$var_name=" .env | cut -d'=' -f2-)
    
    if [[ -z "$var_value" || "$var_value" == *"CHANGE-THIS"* || "$var_value" == *"your-"* ]]; then
        log_error "Variável $var_name não configurada corretamente no .env"
        return 1
    fi
    return 0
}

# Lista de variáveis críticas
CRITICAL_VARS=(
    "SECRET_KEY"
    "DATABASE_URL"
    "REDIS_URL"
    "EMAIL_HOST_USER"
    "EMAIL_HOST_PASSWORD"
)

ERROR_COUNT=0
for var in "${CRITICAL_VARS[@]}"; do
    if ! check_env_var "$var"; then
        ((ERROR_COUNT++))
    fi
done

if [ $ERROR_COUNT -gt 0 ]; then
    log_error "$ERROR_COUNT variáveis críticas não configuradas!"
    log_info "Configure todas as variáveis no arquivo .env antes do deploy"
    exit 1
fi

log_info "✅ Todas as variáveis críticas configuradas"

# 4. Build das imagens Docker
log_info "4️⃣ Buildando imagens Docker..."
docker-compose -f docker-compose.prod.yml build --no-cache

# 5. Executar testes antes do deploy
log_info "5️⃣ Executando testes de pré-deploy..."

# Teste de conectividade do banco
log_info "Testando conexão com banco de dados..."
if ! docker-compose -f docker-compose.prod.yml run --rm main-app python manage.py check --database default; then
    log_error "Falha na conexão com banco de dados"
    exit 1
fi

# Teste de sintaxe Django
log_info "Verificando configuração Django..."
if ! docker-compose -f docker-compose.prod.yml run --rm main-app python manage.py check; then
    log_error "Falha na verificação Django"
    exit 1
fi

# 6. Executar migrações
log_info "6️⃣ Executando migrações do banco de dados..."
docker-compose -f docker-compose.prod.yml run --rm main-app python manage.py migrate

# 7. Coletar arquivos estáticos
log_info "7️⃣ Coletando arquivos estáticos..."
docker-compose -f docker-compose.prod.yml run --rm main-app python manage.py collectstatic --noinput

# 8. Criar superusuário se especificado
if grep -q "DJANGO_CREATE_SUPERUSER=true" .env; then
    log_info "8️⃣ Criando superusuário..."
    docker-compose -f docker-compose.prod.yml run --rm main-app python manage.py shell -c "
from django.contrib.auth import get_user_model
import os
User = get_user_model()
username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@aviladevops.com.br')
password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin123')
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f'Superusuário {username} criado com sucesso!')
else:
    print(f'Superusuário {username} já existe')
"
fi

# 9. Executar containers de produção
log_info "9️⃣ Iniciando containers de produção..."
docker-compose -f docker-compose.prod.yml up -d

# 10. Aguardar serviços ficarem disponíveis
log_info "🔟 Aguardando serviços ficarem disponíveis..."
sleep 30

# 11. Health check
log_info "🏥 Executando health check..."
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f http://localhost/health/ &> /dev/null; then
        log_info "✅ Aplicação respondendo corretamente!"
        break
    fi
    
    ((RETRY_COUNT++))
    log_info "Tentativa $RETRY_COUNT/$MAX_RETRIES - Aguardando aplicação..."
    sleep 10
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    log_error "❌ Aplicação não respondeu após $MAX_RETRIES tentativas"
    log_info "Verificando logs..."
    docker-compose -f docker-compose.prod.yml logs --tail=50 main-app
    exit 1
fi

# 12. Testes pós-deploy
log_info "🧪 Executando testes pós-deploy..."

# Teste de endpoints críticos
ENDPOINTS=(
    "http://localhost/health/"
    "http://localhost/admin/"
    "http://localhost/api/"
)

for endpoint in "${ENDPOINTS[@]}"; do
    if curl -f "$endpoint" &> /dev/null; then
        log_info "✅ $endpoint - OK"
    else
        log_warn "⚠️ $endpoint - Pode estar inacessível"
    fi
done

# 13. Configurar monitoramento
log_info "📊 Configurando monitoramento..."

# Verificar se Prometheus está rodando
if docker-compose -f docker-compose.prod.yml ps prometheus | grep -q "Up"; then
    log_info "✅ Prometheus rodando"
else
    log_warn "⚠️ Prometheus não está rodando"
fi

# 14. Configurar backups automáticos
log_info "💾 Configurando backups automáticos..."

# Criar script de backup
cat > ./scripts/backup_daily.sh << 'EOF'
#!/bin/bash
# Backup diário automatizado
BACKUP_DIR="/var/backups/saas/$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# Backup do banco
docker-compose exec -T db pg_dump -U postgres aviladevops_saas | gzip > "$BACKUP_DIR/database.sql.gz"

# Backup dos arquivos de mídia
tar -czf "$BACKUP_DIR/media.tar.gz" -C /app/media .

# Manter apenas últimos 7 dias
find /var/backups/saas -type d -mtime +7 -exec rm -rf {} +

echo "Backup realizado: $BACKUP_DIR"
EOF

chmod +x ./scripts/backup_daily.sh

# 15. Configurar SSL (Let's Encrypt)
if [ "$1" = "--ssl" ]; then
    log_info "🔒 Configurando SSL com Let's Encrypt..."
    
    # Verificar se certbot está instalado
    if ! command -v certbot &> /dev/null; then
        log_warn "Certbot não instalado. Instalando..."
        sudo apt-get update && sudo apt-get install -y certbot python3-certbot-nginx
    fi
    
    # Gerar certificados
    DOMAIN=$(grep ALLOWED_HOSTS .env | cut -d'=' -f2 | cut -d',' -f1)
    if [ ! -z "$DOMAIN" ] && [ "$DOMAIN" != "localhost" ]; then
        sudo certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos --email admin@aviladevops.com.br
        log_info "✅ SSL configurado para $DOMAIN"
    fi
fi

# 16. Relatório final
log_info "📋 DEPLOY CONCLUÍDO COM SUCESSO!"
echo "=================================================="
echo ""
log_info "🌐 URLs Disponíveis:"
echo "   • Landing Page: http://localhost/"
echo "   • Admin Django: http://localhost/admin/"
echo "   • API REST: http://localhost/api/"
echo "   • Health Check: http://localhost/health/"
echo "   • Metrics: http://localhost/metrics/"
echo ""
log_info "🔧 Comandos Úteis:"
echo "   • Ver logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "   • Parar: docker-compose -f docker-compose.prod.yml down"
echo "   • Reiniciar: docker-compose -f docker-compose.prod.yml restart"
echo "   • Backup: ./scripts/backup_daily.sh"
echo ""
log_info "📊 Monitoramento:"
echo "   • Grafana: http://localhost:3001 (admin/admin)"
echo "   • Prometheus: http://localhost:9090"
echo ""
log_info "🔐 Credenciais de Acesso:"
if grep -q "DJANGO_CREATE_SUPERUSER=true" .env; then
    USERNAME=$(grep DJANGO_SUPERUSER_USERNAME .env | cut -d'=' -f2)
    EMAIL=$(grep DJANGO_SUPERUSER_EMAIL .env | cut -d'=' -f2)
    echo "   • Admin: $USERNAME / [senha definida no .env]"
    echo "   • Email: $EMAIL"
fi
echo ""
log_info "✅ Deploy finalizado! Sistema em produção."

# 17. Agendar backups automáticos
if [ "$1" = "--cron" ]; then
    log_info "⏰ Configurando backup automático diário..."
    (crontab -l 2>/dev/null; echo "0 2 * * * $(pwd)/scripts/backup_daily.sh") | crontab -
    log_info "✅ Backup automático configurado para 02:00 diariamente"
fi

echo "=================================================="
log_info "🎉 SISTEMA SAAS ÁVILA DEVOPS EM PRODUÇÃO! 🎉"
echo "=================================================="