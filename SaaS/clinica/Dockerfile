# Ávila DevOps SaaS - Clínica Management Dockerfile
# Dockerfile padrão para desenvolvimento

FROM node:18-alpine

# Instalar dependências necessárias
RUN apk add --no-cache \
    libc6-compat \
    libjpeg-turbo-dev \
    libpng-dev \
    dumb-init

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências
COPY package*.json ./

# Instalar dependências
RUN npm ci

# Copiar código fonte
COPY . .

# Definir variáveis de ambiente
ENV NEXT_TELEMETRY_DISABLED 1
ENV NODE_ENV development

# Expor porta
EXPOSE 3000

# Comando para iniciar em desenvolvimento
CMD ["npm", "run", "dev"]
