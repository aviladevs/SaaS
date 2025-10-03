# Use uma imagem base oficial do Python
FROM python:3.9-slim

# Defina o diretório de trabalho
WORKDIR /app

# Copie os arquivos necessários para o container
COPY . /app
w
# Instale as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Exponha a porta que o serviço irá usa
EXPOSE 8080

# Comando para iniciar o servidor
CMD ["gunicorn", "wsgi:application", "--bind", "0.0.0.0:8080"]