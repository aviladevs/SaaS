# Multi-stage build para serviço Django
FROM python:3.11-slim as base

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root
RUN groupadd -r appuser && useradd -r -g appuser appuser

FROM base as dependencies

# Instalar Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

FROM dependencies as build

# Copiar código fonte
WORKDIR /app
COPY . .

# Coletar arquivos estáticos
RUN python manage.py collectstatic --noinput --clear

FROM base as production

# Configurar usuário não-root
RUN mkdir -p /app && chown -R appuser:appuser /app
WORKDIR /app

# Copiar dependências instaladas
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copiar código da aplicação
COPY --chown=appuser:appuser . .

# Tornar usuário owner dos arquivos
RUN chown -R appuser:appuser /app

# Mudar para usuário não-root
USER appuser

# Expor porta (definir via variável de ambiente)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Comando de inicialização (porta definida via variável de ambiente)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--chdir", "/app", "service.wsgi:application"]
