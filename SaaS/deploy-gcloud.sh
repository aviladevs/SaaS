#!/bin/bash

echo "🚀 DEPLOY PARA GOOGLE CLOUD APP ENGINE"
echo "====================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar se gcloud está instalado
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Google Cloud SDK não encontrado!${NC}"
    echo "Instale: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo -e "${YELLOW}📋 Verificando configuração...${NC}"

# Verificar se está logado no gcloud
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo -e "${YELLOW}🔐 Fazendo login no Google Cloud...${NC}"
    gcloud auth login
fi

# Configurar projeto
echo -e "${YELLOW}🔧 Configurando projeto...${NC}"
gcloud config set project principaldevops

# Habilitar APIs necessárias
echo -e "${YELLOW}🔌 Habilitando APIs necessárias...${NC}"
gcloud services enable appengine.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com

# Coletar arquivos estáticos
echo -e "${YELLOW}📁 Coletando arquivos estáticos...${NC}"
cd "d:\Dev Driver\SaaS\SaaS\app-aviladevops"
python manage.py collectstatic --noinput

# Fazer migrações
echo -e "${YELLOW}🗄️ Executando migrações...${NC}"
python manage.py migrate --noinput

# Deploy para App Engine
echo -e "${YELLOW}🚀 Fazendo deploy para App Engine...${NC}"
gcloud app deploy app.yaml --quiet

# Verificar se o deploy foi bem-sucedido
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Deploy realizado com sucesso!${NC}"
    
    # Obter URL da aplicação
    APP_URL=$(gcloud app describe --format="value(defaultHostname)")
    echo -e "${GREEN}🌐 Aplicação disponível em: https://${APP_URL}${NC}"
    echo -e "${GREEN}🔗 Admin: https://${APP_URL}/admin${NC}"
    echo -e "${GREEN}📊 API: https://${APP_URL}/api${NC}"
    
    echo ""
    echo -e "${YELLOW}👤 CREDENCIAIS:${NC}"
    echo "   • Usuário: admin"
    echo "   • Senha: admin123"
    echo ""
    
    # Abrir aplicação no navegador
    echo -e "${YELLOW}🌐 Abrindo aplicação...${NC}"
    gcloud app browse
else
    echo -e "${RED}❌ Erro durante o deploy!${NC}"
    exit 1
fi

echo -e "${GREEN}🎉 DEPLOY CONCLUÍDO COM SUCESSO!${NC}"