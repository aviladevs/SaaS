# Ávila DevOps SaaS - Makefile
# Automação para desenvolvimento, testes e deploy

.PHONY: help install dev test deploy clean backup monitor logs

# Default target
help:
	@echo "🚀 Ávila DevOps SaaS - Comandos disponíveis:"
	@echo ""
	@echo "💻 Desenvolvimento:"
	@echo "  make install      - Instala dependências"
	@echo "  make dev          - Inicia ambiente de desenvolvimento"
	@echo "  make test         - Executa testes"
	@echo "  make lint         - Verifica qualidade do código"
	@echo ""
	@echo "🏗️  Build & Deploy:"
	@echo "  make build        - Builda imagens Docker"
	@echo "  make deploy-dev   - Deploy para desenvolvimento"
	@echo "  make deploy-staging - Deploy para homologação"
	@echo "  make deploy-prod  - Deploy para produção"
	@echo ""
	@echo "📊 Monitoramento:"
	@echo "  make monitor         - Inicia stack de monitoramento"
	@echo "  make monitor-stop    - Para stack de monitoramento"
	@echo "  make monitor-restart - Reinicia stack de monitoramento"
	@echo "  make monitor-status  - Status dos serviços de monitoramento"
	@echo "  make monitor-logs    - Visualiza logs do monitoramento"
	@echo "  make monitor-health  - Health check do monitoramento"
	@echo ""
	@echo "🔧 Manutenção:"
	@echo "  make clean        - Limpa arquivos temporários"
	@echo "  make backup       - Cria backup completo"
	@echo "  make restore      - Restaura backup"
	@echo "  make logs         - Visualiza logs"
	@echo ""
	@echo "👥 Tenants:"
	@echo "  make tenant-create - Cria novo tenant"
	@echo "  make tenant-list   - Lista tenants"
	@echo "  make tenant-backup - Backup de tenant"

# Instala dependências
install:
	@echo "📦 Instalando dependências..."
	@pip install -r requirements.txt
	@cd clinica && npm install
	@echo "✅ Dependências instaladas!"

# Ambiente de desenvolvimento
dev:
	@echo "🚀 Iniciando ambiente de desenvolvimento..."
	@docker-compose -f docker-compose.saas.yml up -d
	@echo "✅ Ambiente iniciado!"
	@echo "🌐 Landing Page: http://localhost:8000"
	@echo "🏭 Sistema: http://localhost:8001"
	@echo "📊 Fiscal: http://localhost:8002"
	@echo "🏥 Clínica: http://localhost:3000"
	@echo "⚙️  Admin: http://localhost:8003"

# Executa testes
test:
	@echo "🧪 Executando testes..."
	@python -m pytest --cov=. --cov-report=html
	@echo "✅ Testes concluídos!"

# Verifica qualidade do código
lint:
	@echo "🔍 Verificando qualidade do código..."
	@black --check .
	@flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	@flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
	@echo "✅ Verificação concluída!"

# Build das imagens Docker
build:
	@echo "🏗️  Buildando imagens Docker..."
	@docker-compose -f docker-compose.saas.yml build
	@echo "✅ Build concluído!"

# Deploy para desenvolvimento
deploy-dev:
	@echo "🚀 Deploy para desenvolvimento..."
	@docker-compose -f docker-compose.saas.yml up -d --build
	@echo "✅ Deploy concluído!"

# Deploy para staging
deploy-staging:
	@echo "🏗️  Deploy para homologação..."
	@terraform -chdir=terraform workspace select staging || terraform -chdir=terraform workspace new staging
	@terraform -chdir=terraform plan -var environment=staging
	@terraform -chdir=terraform apply -var environment=staging -auto-approve
	@echo "✅ Deploy para staging concluído!"

# Deploy para produção
deploy-prod:
	@echo "🚀 Deploy para produção..."
	@terraform -chdir=terraform workspace select production || terraform -chdir=terraform workspace new production
	@terraform -chdir=terraform plan -var environment=production
	@terraform -chdir=terraform apply -var environment=production -auto-approve
	@kubectl apply -f kubernetes/saas-deployment.yaml
	@echo "✅ Deploy para produção concluído!"

# Limpa arquivos temporários
clean:
	@echo "🧹 Limpando arquivos temporários..."
	@find . -type d -name __pycache__ -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@find . -name "*.pyc" -delete
	@find . -name "*.pyo" -delete
	@find . -name "*.pyd" -delete
	@docker system prune -f
	@echo "✅ Limpeza concluída!"

# Cria backup completo
backup:
	@echo "💾 Criando backup completo..."
	@python scripts/backup_manager.py create-full-backup
	@echo "✅ Backup criado!"

# Restaura backup
restore:
	@echo "🔄 Restaurando backup..."
	@python scripts/backup_manager.py restore-latest
	@echo "✅ Restauração concluída!"

# Inicia monitoramento
monitor:
	@echo "📊 Iniciando stack de monitoramento..."
	@bash monitoring/start-monitoring.sh

# Para monitoramento
monitor-stop:
	@echo "⏹️  Parando stack de monitoramento..."
	@docker-compose -f docker-compose.monitoring.yml down
	@echo "✅ Monitoramento parado!"

# Reinicia monitoramento
monitor-restart:
	@echo "🔄 Reiniciando stack de monitoramento..."
	@docker-compose -f docker-compose.monitoring.yml restart
	@echo "✅ Monitoramento reiniciado!"

# Status do monitoramento
monitor-status:
	@echo "📊 Status do monitoramento:"
	@docker-compose -f docker-compose.monitoring.yml ps

# Logs do monitoramento
monitor-logs:
	@docker-compose -f docker-compose.monitoring.yml logs -f

# Health check do monitoramento
monitor-health:
	@bash monitoring/start-monitoring.sh health

# Visualiza logs
logs:
	@echo "📋 Visualizando logs..."
	@docker-compose -f docker-compose.saas.yml logs -f

# Gestão de tenants
tenant-create:
	@echo "👥 Criando novo tenant..."
	@python scripts/tenant_management.py create \
		--name $(shell read -p "Nome do tenant: " tenant; echo $$tenant) \
		--domain $(shell read -p "Domínio: " domain; echo $$domain) \
		--owner-email $(shell read -p "Email do owner: " email; echo $$email)

tenant-list:
	@echo "📋 Listando tenants..."
	@python scripts/tenant_management.py list

tenant-backup:
	@echo "💾 Fazendo backup de tenant..."
	@python scripts/tenant_management.py backup \
		--name $(shell read -p "Nome do tenant: " tenant; echo $$tenant)

# Database operations
migrate:
	@echo "🗄️  Executando migrações..."
	@docker-compose -f docker-compose.saas.yml exec main-app python manage.py migrate
	@docker-compose -f docker-compose.saas.yml exec recycling-system python manage.py migrate
	@docker-compose -f docker-compose.saas.yml exec fiscal-system python manage.py migrate
	@echo "✅ Migrações concluídas!"

makemigrations:
	@echo "📝 Criando migrações..."
	@docker-compose -f docker-compose.saas.yml exec main-app python manage.py makemigrations
	@echo "✅ Migrações criadas!"

shell:
	@echo "🐚 Iniciando shell Django..."
	@docker-compose -f docker-compose.saas.yml exec main-app python manage.py shell

# Superuser creation
superuser:
	@echo "👑 Criando superusuário..."
	@docker-compose -f docker-compose.saas.yml exec main-app python manage.py createsuperuser

# Static files collection
collectstatic:
	@echo "📁 Coletando arquivos estáticos..."
	@docker-compose -f docker-compose.saas.yml exec main-app python manage.py collectstatic --noinput
	@echo "✅ Arquivos estáticos coletados!"

# Health check
health:
	@echo "🏥 Verificando saúde dos serviços..."
	@curl -f http://localhost:8000/health/ && echo "✅ Landing Page OK" || echo "❌ Landing Page FAIL"
	@curl -f http://localhost:8001/health/ && echo "✅ Sistema OK" || echo "❌ Sistema FAIL"
	@curl -f http://localhost:8002/health/ && echo "✅ Fiscal OK" || echo "❌ Fiscal FAIL"
	@curl -f http://localhost:3000/health/ && echo "✅ Clínica OK" || echo "❌ Clínica FAIL"
	@echo "🏥 Verificação concluída!"

# Performance testing
perf-test:
	@echo "⚡ Executando testes de performance..."
	@lighthouse http://localhost:8000 --output html --output-path ./reports/landing-page-perf.html
	@echo "✅ Testes de performance concluídos!"

# Security scan
security-scan:
	@echo "🔒 Executando scan de segurança..."
	@safety check
	@bandit -r . -f json -o reports/security-report.json
	@echo "✅ Scan de segurança concluído!"

# Documentation
docs-serve:
	@echo "📚 Servindo documentação..."
	@mkdocs serve

docs-build:
	@echo "📚 Buildando documentação..."
	@mkdocs build

# Release management
release-patch:
	@echo "📦 Criando release patch..."
	@bump2version patch
	@git push --follow-tags

release-minor:
	@echo "📦 Criando release minor..."
	@bump2version minor
	@git push --follow-tags

release-major:
	@echo "📦 Criando release major..."
	@bump2version major
	@git push --follow-tags

# Environment specific commands
dev-setup: install migrate superuser collectstatic
staging-setup: deploy-staging health
prod-setup: deploy-prod health

# Database maintenance
db-backup:
	@echo "💾 Backup do banco de dados..."
	@docker-compose -f docker-compose.saas.yml exec db pg_dump -U postgres aviladevops_saas > backups/db-$(shell date +%Y%m%d-%H%M%S).sql

db-restore:
	@echo "🔄 Restaurando banco de dados..."
	@docker-compose -f docker-compose.saas.yml exec -T db psql -U postgres aviladevops_saas < $(shell ls -t backups/db-*.sql | head -1)

# Cache management
cache-clear:
	@echo "🧹 Limpando cache..."
	@docker-compose -f docker-compose.saas.yml exec redis redis-cli FLUSHALL
	@echo "✅ Cache limpo!"

# Log rotation
log-rotate:
	@echo "📜 Rotacionando logs..."
	@docker-compose -f docker-compose.saas.yml logs --no-log-prefix > logs/combined-$(shell date +%Y%m%d-%H%M%S).log
	@echo "✅ Logs rotacionados!"

# Container management
restart-services:
	@echo "🔄 Reiniciando serviços..."
	@docker-compose -f docker-compose.saas.yml restart
	@echo "✅ Serviços reiniciados!"

stop-services:
	@echo "⏹️  Parando serviços..."
	@docker-compose -f docker-compose.saas.yml down
	@echo "✅ Serviços parados!"

# Dependency updates
update-deps:
	@echo "⬆️  Atualizando dependências..."
	@pip-compile requirements.in
	@pip install -r requirements.txt
	@echo "✅ Dependências atualizadas!"

# Code formatting
format:
	@echo "🎨 Formatando código..."
	@black .
	@isort .
	@echo "✅ Código formatado!"

# Type checking
type-check:
	@echo "🔍 Verificando tipos..."
	@mypy .
	@echo "✅ Verificação de tipos concluída!"

# All checks
check-all: lint test type-check security-scan
	@echo "✅ Todas as verificações concluídas!"
