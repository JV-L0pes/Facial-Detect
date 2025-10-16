@echo off
echo ========================================
echo Sistema de Reconhecimento Facial
echo ========================================
echo.

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

if errorlevel 1 (
    echo ERRO: Ambiente virtual nao encontrado!
    echo Execute o setup primeiro.
    pause
    exit /b 1
)

echo OK: Ambiente virtual ativado
echo.

echo Iniciando servidor...
echo Acesse: http://localhost:8000
echo Pressione Ctrl+C para parar
echo.

python backend\app\main.py

pause
