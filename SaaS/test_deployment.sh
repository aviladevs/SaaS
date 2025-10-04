#!/bin/bash

echo "🧪 TESTE FINAL DE DEPLOYMENT - GOOGLE CLOUD"
echo "=========================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_ID="principaldevops"

echo -e "${BLUE}📋 INICIANDO VERIFICAÇÕES...${NC}"

# 1. Verificar autenticação
echo -e "\n${YELLOW}1️⃣ Verificando autenticação...${NC}"
if gcloud auth list --filter=status:ACTIVE --format="value(account)" >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Autenticação OK${NC}"
else
    echo -e "${RED}❌ Problema de autenticação${NC}"
    exit 1
fi

# 2. Verificar projeto
echo -e "\n${YELLOW}2️⃣ Verificando projeto...${NC}"
CURRENT_PROJECT=$(gcloud config get-value project)
if [ "$CURRENT_PROJECT" = "$PROJECT_ID" ]; then
    echo -e "${GREEN}✅ Projeto correto: $PROJECT_ID${NC}"
else
    echo -e "${RED}❌ Projeto incorreto: $CURRENT_PROJECT (esperado: $PROJECT_ID)${NC}"
    exit 1
fi

# 3. Verificar APIs habilitadas
echo -e "\n${YELLOW}3️⃣ Verificando APIs necessárias...${NC}"
REQUIRED_APIS=("run.googleapis.com" "cloudbuild.googleapis.com" "kms.googleapis.com")
MISSING_APIS=()

for api in "${REQUIRED_APIS[@]}"; do
    if gcloud services list --enabled | grep -q "$api"; then
        echo -e "${GREEN}✅ $api habilitada${NC}"
    else
        echo -e "${RED}❌ $api não habilitada${NC}"
        MISSING_APIS+=("$api")
    fi
done

if [ ${#MISSING_APIS[@]} -gt 0 ]; then
    echo -e "${YELLOW}🔧 Habilitando APIs faltantes...${NC}"
    for api in "${MISSING_APIS[@]}"; do
        gcloud services enable "$api"
    done
fi

# 4. Verificar chave KMS
echo -e "\n${YELLOW}4️⃣ Verificando chave KMS...${NC}"
if gcloud kms keys describe saas-database-key \
    --keyring saas-nfe-keyring \
    --location global \
    --project $PROJECT_ID >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Chave KMS existe${NC}"
else
    echo -e "${RED}❌ Chave KMS não encontrada${NC}"
    echo -e "${YELLOW}🔧 Execute: bash fix_kms_config.sh${NC}"
    exit 1
fi

# 5. Verificar Dockerfiles
echo -e "\n${YELLOW}5️⃣ Verificando Dockerfiles...${NC}"
SERVICES=("LANDING-PAGE" "sistema" "fiscal/web_app" "clinica")
INVALID_DOCKERFILES=()

for service in "${SERVICES[@]}"; do
    dockerfile="$service/Dockerfile"
    if [ -f "$dockerfile" ]; then
        # Verificar se tem erros básicos
        if grep -q "^w$" "$dockerfile" 2>/dev/null; then
            echo -e "${RED}❌ $dockerfile tem erro de sintaxe${NC}"
            INVALID_DOCKERFILES+=("$service")
        else
            echo -e "${GREEN}✅ $dockerfile OK${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️ $dockerfile não encontrado${NC}"
    fi
done

# 6. Teste básico de build
echo -e "\n${YELLOW}6️⃣ Testando build básico...${NC}"
cd LANDING-PAGE
if docker build -t test-landing-page . >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Build da Landing Page OK${NC}"
    docker rmi test-landing-page >/dev/null 2>&1
else
    echo -e "${RED}❌ Problema no build da Landing Page${NC}"
fi
cd ..

# 7. Verificar permissões básicas
echo -e "\n${YELLOW}7️⃣ Verificando permissões básicas...${NC}"
USER_EMAIL=$(gcloud auth list --filter=status:ACTIVE --format="value(account)")
if gcloud projects get-iam-policy $PROJECT_ID --format="table(bindings.role)" | grep -q "roles/owner"; then
    echo -e "${GREEN}✅ Você tem permissões de owner${NC}"
else
    echo -e "${YELLOW}⚠️ Verifique suas permissões no projeto${NC}"
fi

# 8. Teste de deploy simples (opcional)
echo -e "\n${YELLOW}8️⃣ Teste de deploy (opcional)...${NC}"
read -p "Deseja testar um deploy simples? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}🚀 Fazendo deploy de teste da Landing Page...${NC}"
    if timeout 300 gcloud run deploy landing-page-test \
        --source LANDING-PAGE \
        --platform managed \
        --region southamerica-east1 \
        --allow-unauthenticated \
        --port 8080; then
        echo -e "${GREEN}✅ Deploy de teste realizado com sucesso!${NC}"

        # Obter URL
        SERVICE_URL=$(gcloud run services describe landing-page-test \
            --platform managed \
            --region southamerica-east1 \
            --format="value(status.url)" 2>/dev/null)

        if [ -n "$SERVICE_URL" ]; then
            echo -e "${GREEN}🌐 Serviço disponível em: $SERVICE_URL${NC}"
        fi

        # Limpar serviço de teste
        gcloud run services delete landing-page-test \
            --platform managed \
            --region southamerica-east1 \
            --quiet 2>/dev/null
    else
        echo -e "${RED}❌ Problemas no deploy de teste${NC}"
    fi
fi

echo -e "\n${BLUE}📊 RESUMO DO TESTE${NC}"
echo -e "${BLUE}================${NC}"

if [ ${#INVALID_DOCKERFILES[@]} -eq 0 ] && [ ${#MISSING_APIS[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ Ambiente parece estar configurado corretamente${NC}"
    echo -e "${GREEN}🎉 Pronto para deploy!${NC}"
    echo -e "\n${YELLOW}💡 Para fazer o deploy completo:${NC}"
    echo "   python deploy_services_v2.py"
else
    echo -e "${YELLOW}⚠️ Alguns problemas ainda precisam ser resolvidos${NC}"
    echo -e "\n${YELLOW}🔧 Correções necessárias:${NC}"
    [ ${#INVALID_DOCKERFILES[@]} -gt 0 ] && echo "   - Corrigir Dockerfiles: ${INVALID_DOCKERFILES[*]}"
    [ ${#MISSING_APIS[@]} -gt 0 ] && echo "   - Habilitar APIs: ${MISSING_APIS[*]}"
fi
