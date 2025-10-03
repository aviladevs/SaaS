@echo off
echo ========================================
echo   DEPLOY - GOOGLE CLOUD PLATFORM
echo ========================================
echo.

echo [1/5] Coletando arquivos estaticos...
python manage.py collectstatic --noinput --settings=xml_manager.settings_production

echo.
echo [2/5] Verificando configuracao...
python manage.py check --deploy --settings=xml_manager.settings_production

echo.
echo [3/5] Testando migracao...
echo (Pulando migracao - execute depois do deploy com: gcloud app deploy --promote)

echo.
echo [4/5] Fazendo deploy no App Engine...
gcloud app deploy app.yaml --quiet --stop-previous-version

echo.
echo [5/5] Abrindo aplicacao...
gcloud app browse

echo.
echo ========================================
echo   DEPLOY CONCLUIDO!
echo ========================================

