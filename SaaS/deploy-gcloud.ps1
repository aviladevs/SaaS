# 🚀 DEPLOY PARA GOOGLE CLOUD APP ENGINE - WINDOWS
# =====================================================

Write-Host "🚀 DEPLOY PARA GOOGLE CLOUD APP ENGINE" -ForegroundColor Yellow
Write-Host "======================================"

# Verificar se gcloud está instalado
try {
    $gcloudVersion = gcloud version
    Write-Host "✅ Google Cloud SDK encontrado" -ForegroundColor Green
} catch {
    Write-Host "❌ Google Cloud SDK não encontrado!" -ForegroundColor Red
    Write-Host "Instale: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

Write-Host "📋 Verificando configuração..." -ForegroundColor Yellow

# Verificar se está logado no gcloud
$activeAccount = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null
if (-not $activeAccount) {
    Write-Host "🔐 Fazendo login no Google Cloud..." -ForegroundColor Yellow
    gcloud auth login
}

# Configurar projeto
Write-Host "🔧 Configurando projeto..." -ForegroundColor Yellow
gcloud config set project principaldevops

# Habilitar APIs necessárias
Write-Host "🔌 Habilitando APIs necessárias..." -ForegroundColor Yellow
gcloud services enable appengine.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com

# Navegar para o diretório da aplicação
Set-Location "d:\Dev Driver\SaaS\SaaS\app-aviladevops"

# Coletar arquivos estáticos
Write-Host "📁 Coletando arquivos estáticos..." -ForegroundColor Yellow
python manage.py collectstatic --noinput

# Fazer migrações
Write-Host "🗄️ Executando migrações..." -ForegroundColor Yellow
python manage.py migrate --noinput

# Deploy para App Engine
Write-Host "🚀 Fazendo deploy para App Engine..." -ForegroundColor Yellow
gcloud app deploy app.yaml --quiet

# Verificar se o deploy foi bem-sucedido
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Deploy realizado com sucesso!" -ForegroundColor Green
    
    # Obter URL da aplicação
    $appUrl = gcloud app describe --format="value(defaultHostname)"
    Write-Host "🌐 Aplicação disponível em: https://$appUrl" -ForegroundColor Green
    Write-Host "🔗 Admin: https://$appUrl/admin" -ForegroundColor Green
    Write-Host "📊 API: https://$appUrl/api" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "👤 CREDENCIAIS:" -ForegroundColor Yellow
    Write-Host "   • Usuário: admin"
    Write-Host "   • Senha: admin123"
    Write-Host ""
    
    # Abrir aplicação no navegador
    Write-Host "🌐 Abrindo aplicação..." -ForegroundColor Yellow
    gcloud app browse
} else {
    Write-Host "❌ Erro durante o deploy!" -ForegroundColor Red
    exit 1
}

Write-Host "🎉 DEPLOY CONCLUÍDO COM SUCESSO!" -ForegroundColor Green