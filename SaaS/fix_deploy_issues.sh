#!/bin/bash

echo "🔧 CORRIGINDO PROBLEMAS COMUNS DE DEPLOY"
echo "======================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para verificar e corrigir Dockerfile
fix_dockerfile() {
    local service_path="$1"
    local dockerfile="$service_path/Dockerfile"

    if [ -f "$dockerfile" ]; then
        echo -e "${YELLOW}🔍 Verificando Dockerfile em: $dockerfile${NC}"

        # Verificar se há erros comuns
        if grep -q "^w$" "$dockerfile"; then
            echo -e "${YELLOW}⚠️ Encontrado erro no Dockerfile (linha 'w' solta)${NC}"
            # Remover linha problemática
            sed -i '/^w$/d' "$dockerfile"
            echo -e "${GREEN}✅ Linha problemática removida${NC}"
        fi

        # Verificar estrutura básica
        if ! grep -q "FROM python" "$dockerfile" && ! grep -q "FROM node" "$dockerfile"; then
            echo -e "${RED}❌ Dockerfile não tem instrução FROM válida${NC}"
            return 1
        fi

        if ! grep -q "EXPOSE" "$dockerfile"; then
            echo -e "${RED}❌ Dockerfile não tem instrução EXPOSE${NC}"
            return 1
        fi

        echo -e "${GREEN}✅ Dockerfile parece estar correto${NC}"
        return 0
    else
        echo -e "${RED}❌ Dockerfile não encontrado em: $dockerfile${NC}"
        return 1
    fi
}

# Verificar serviços
services=("LANDING-PAGE" "sistema" "fiscal/web_app" "clinica")

for service in "${services[@]}"; do
    echo -e "\n${YELLOW}📋 Verificando serviço: $service${NC}"
    fix_dockerfile "$service"
done

echo -e "\n${GREEN}🎉 VERIFICAÇÃO CONCLUÍDA!${NC}"
echo -e "${YELLOW}💡 Para fazer o deploy, execute:${NC}"
echo "   python deploy_services_v2.py"
