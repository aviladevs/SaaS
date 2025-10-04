# Imagem base leve
FROM python:3.11-slim

# Variáveis de ambiente para otimização
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema (caso precise compilar pacotes)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro (cache eficiente)
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --upgrade pip && pip install -r requirements.txt gunicorn

# Copiar código do projeto
COPY . .

# Usuário não-root para segurança
RUN useradd -m appuser
USER appuser

# Cloud Run usa porta 8080
EXPOSE 8080

# Comando para rodar o Django com Gunicorn
# Ajuste `xml_manager.wsgi:application` para o caminho do seu wsgi.py
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "xml_manager.wsgi:application"]