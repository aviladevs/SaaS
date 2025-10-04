@echo off
echo ========================================
echo   XML MANAGER - SETUP SIMPLES
echo ========================================
echo.

echo [1/4] Instalando dependencias minimas...
pip install Django==4.2.7 djangorestframework==3.14.0 django-cors-headers==4.3.1

echo.
echo [2/4] Criando banco de dados...
python manage.py makemigrations core
python manage.py makemigrations api
python manage.py migrate

echo.
echo [3/4] Criando superusuario...
echo.
echo Digite os dados do superusuario:
python manage.py createsuperuser

echo.
echo [4/4] Coletando arquivos estaticos...
python manage.py collectstatic --noinput

echo.
echo ========================================
echo   SETUP CONCLUIDO!
echo ========================================
echo.
echo Para iniciar o servidor:
echo   python manage.py runserver
echo.
echo Acesse: http://localhost:8000
echo.
pause
