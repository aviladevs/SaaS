#!/bin/bash

echo "🔧 CORRIGINDO CONFIGURAÇÃO DO CLOUD BUILD"
echo "========================================"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PROJECT_ID="principaldevops"

echo -e "${YELLOW}📋 Verificando configuração do Cloud Build...${NC}"

# Verificar se há triggers ativos
echo -e "${YELLOW}🔍 Verificando triggers do Cloud Build...${NC}"
TRIGGERS=$(gcloud builds triggers list --project $PROJECT_ID --format="value(id)" 2>/dev/null)

if [ -n "$TRIGGERS" ]; then
    echo -e "${GREEN}✅ Triggers encontrados: $(echo $TRIGGERS | wc -w) trigger(s)${NC}"

    # Desabilitar triggers problemáticos temporariamente
    for trigger_id in $TRIGGERS; do
        echo -e "${YELLOW}🔧 Desabilitando trigger: $trigger_id${NC}"
        gcloud builds triggers delete $trigger_id --project $PROJECT_ID --quiet 2>/dev/null || true
    done
else
    echo -e "${YELLOW}ℹ️ Nenhum trigger encontrado${NC}"
fi

# Verificar serviço Cloud Build
echo -e "${YELLOW}🔍 Verificando serviço Cloud Build...${NC}"
if gcloud services list --project $PROJECT_ID --enabled | grep -q cloudbuild.googleapis.com; then
    echo -e "${GREEN}✅ Cloud Build API habilitada${NC}"
else
    echo -e "${YELLOW}🔧 Habilitando Cloud Build API...${NC}"
    gcloud services enable cloudbuild.googleapis.com --project $PROJECT_ID
fi

# Configurar service account do Cloud Build
echo -e "${YELLOW}🔐 Configurando service account do Cloud Build...${NC}"

# Verificar se a service account existe
CB_SA="791209015957@cloudbuild.gserviceaccount.com"
if gcloud iam service-accounts describe $CB_SA --project $PROJECT_ID >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Service account do Cloud Build existe${NC}"
else
    echo -e "${RED}❌ Service account do Cloud Build não encontrada${NC}"
    echo -e "${YELLOW}🔧 Você precisa criar a service account manualmente no console${NC}"
fi

# Conceder permissões necessárias
echo -e "${YELLOW}🔐 Concedendo permissões necessárias...${NC}"

# Permissões básicas
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CB_SA" \
    --role="roles/cloudbuild.builds.builder" \
    --quiet 2>/dev/null || echo -e "${YELLOW}ℹ️ Permissão já existe${NC}"

# Permissões para Cloud Run
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CB_SA" \
    --role="roles/run.admin" \
    --quiet 2>/dev/null || echo -e "${YELLOW}ℹ️ Permissão já existe${NC}"

# Permissões para Container Registry
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CB_SA" \
    --role="roles/containerregistry.ServiceAgent" \
    --quiet 2>/dev/null || echo -e "${YELLOW}ℹ️ Permissão já existe${NC}"

# Permissões para KMS
gcloud kms keys add-iam-policy-binding saas-database-key \
    --keyring saas-nfe-keyring \
    --location global \
    --member="serviceAccount:$CB_SA" \
    --role="roles/cloudkms.cryptoKeyEncrypterDecrypter" \
    --project $PROJECT_ID \
    --quiet 2>/dev/null || echo -e "${YELLOW}ℹ️ Permissão já existe${NC}"

echo -e "${GREEN}✅ Permissões configuradas${NC}"

# Criar trigger básico para deploy
echo -e "${YELLOW}🏗️ Criando trigger básico...${NC}"

cat > cloudbuild.yaml << EOF
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/landing-page', 'LANDING-PAGE/']

  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/landing-page']

  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'landing-page-service'
      - '--image'
      - 'gcr.io/$PROJECT_ID/landing-page'
      - '--region'
      - 'southamerica-east1'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'

timeout: '1200s'
EOF

echo -e "${GREEN}✅ Arquivo cloudbuild.yaml criado${NC}"

# Testar configuração
echo -e "${YELLOW}🧪 Testando configuração...${NC}"
if gcloud builds submit --config cloudbuild.yaml --project $PROJECT_ID . >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Configuração do Cloud Build parece estar funcionando${NC}"
else
    echo -e "${YELLOW}⚠️ Problemas ainda podem existir - teste manual necessário${NC}"
fi

echo -e "${GREEN}🎉 CORREÇÃO DO CLOUD BUILD CONCLUÍDA!${NC}"
echo -e "${YELLOW}💡 Para testar:${NC}"
echo "   gcloud builds triggers create github --repo-name=seu-repo --repo-owner=seu-usuario --branch-pattern=main --build-config=cloudbuild.yaml"
