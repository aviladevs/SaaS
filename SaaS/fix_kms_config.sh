#!/bin/bash

echo "🔧 CORRIGINDO CONFIGURAÇÃO DO GOOGLE CLOUD KMS"
echo "=============================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PROJECT_ID="principaldevops"

echo -e "${YELLOW}📋 Verificando configuração atual do KMS...${NC}"

# Verificar se o key ring existe
echo -e "${YELLOW}🔍 Verificando key ring saas-nfe-keyring...${NC}"
if gcloud kms keyrings describe saas-nfe-keyring \
    --location global \
    --project $PROJECT_ID >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Key ring saas-nfe-keyring existe${NC}"
else
    echo -e "${RED}❌ Key ring saas-nfe-keyring não encontrado${NC}"
    echo -e "${YELLOW}🔧 Criando key ring...${NC}"
    gcloud kms keyrings create saas-nfe-keyring \
        --location global \
        --project $PROJECT_ID
fi

# Verificar se a chave existe
echo -e "${YELLOW}🔍 Verificando chave saas-database-key...${NC}"
if gcloud kms keys describe saas-database-key \
    --keyring saas-nfe-keyring \
    --location global \
    --project $PROJECT_ID >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Chave saas-database-key existe${NC}"
else
    echo -e "${RED}❌ Chave saas-database-key não encontrada${NC}"
    echo -e "${YELLOW}🔧 Criando chave...${NC}"
    gcloud kms keys create saas-database-key \
        --keyring saas-nfe-keyring \
        --location global \
        --purpose encryption \
        --project $PROJECT_ID
fi

# Verificar se a versão da chave existe
echo -e "${YELLOW}🔍 Verificando versão da chave...${NC}"
KEY_VERSION=$(gcloud kms keys versions list \
    --key saas-database-key \
    --keyring saas-nfe-keyring \
    --location global \
    --project $PROJECT_ID \
    --format="value(name)" 2>/dev/null | head -1)

if [ -n "$KEY_VERSION" ]; then
    echo -e "${GREEN}✅ Versão da chave existe: $KEY_VERSION${NC}"
else
    echo -e "${YELLOW}🔧 Criando versão da chave...${NC}"
    gcloud kms keys versions create \
        --key saas-database-key \
        --keyring saas-nfe-keyring \
        --location global \
        --project $PROJECT_ID
fi

# Configurar permissões para a chave
echo -e "${YELLOW}🔐 Configurando permissões da chave...${NC}"
gcloud kms keys add-iam-policy-binding saas-database-key \
    --keyring saas-nfe-keyring \
    --location global \
    --member="serviceAccount:791209015957@cloudbuild.gserviceaccount.com" \
    --role="roles/cloudkms.cryptoKeyEncrypterDecrypter" \
    --project $PROJECT_ID

gcloud kms keys add-iam-policy-binding saas-database-key \
    --keyring saas-nfe-keyring \
    --location global \
    --member="user:nicolasrosaab1@gmail.com" \
    --role="roles/cloudkms.cryptoKeyEncrypterDecrypter" \
    --project $PROJECT_ID

echo -e "${GREEN}✅ Permissões configuradas${NC}"

# Atualizar configuração do projeto
echo -e "${YELLOW}📝 Atualizando configuração do projeto...${NC}"
cat > temp_kms_config.json << EOF
{
  "google_cloud": {
    "project_id": "principaldevops",
    "kms": {
      "key_ring": "saas-nfe-keyring",
      "key_name": "saas-database-key",
      "key_uri": "projects/principaldevops/locations/global/keyRings/saas-nfe-keyring/cryptoKeys/saas-database-key"
    }
  }
}
EOF

echo -e "${GREEN}✅ Configuração do KMS corrigida!${NC}"
echo -e "${YELLOW}💡 Execute este comando para testar:${NC}"
echo "   gcloud kms encrypt --key saas-database-key --keyring saas-nfe-keyring --location global --plaintext-file=<(echo 'teste') --ciphertext-file=- --project principaldevops | base64"

rm -f temp_kms_config.json
