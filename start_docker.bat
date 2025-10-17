@echo off
echo ========================================
echo Sistema de Reconhecimento Facial
echo Docker Setup
echo ========================================

REM Verificar se Docker está instalado
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker não está instalado!
    echo Por favor, instale o Docker Desktop primeiro: https://docs.docker.com/desktop/windows/
    pause
    exit /b 1
)

REM Verificar se Docker Compose está instalado
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose não está instalado!
    echo Por favor, instale o Docker Desktop primeiro: https://docs.docker.com/desktop/windows/
    pause
    exit /b 1
)

echo ✅ Docker e Docker Compose encontrados!

REM Criar diretórios necessários
echo 📁 Criando diretórios...
if not exist data\faiss_index mkdir data\faiss_index
if not exist data\logs mkdir data\logs
if not exist logs mkdir logs

REM Construir e iniciar containers
echo 🔨 Construindo containers...
docker-compose build

echo 🚀 Iniciando serviços...
docker-compose up -d

REM Aguardar serviços ficarem prontos
echo ⏳ Aguardando serviços ficarem prontos...
timeout /t 10 /nobreak >nul

REM Verificar status
echo 📊 Status dos serviços:
docker-compose ps

echo.
echo ========================================
echo ✅ Sistema iniciado com sucesso!
echo.
echo 🌐 Frontend: http://localhost
echo 🔧 Backend API: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo.
echo 📋 Comandos úteis:
echo   - Ver logs: docker-compose logs -f
echo   - Parar: docker-compose down
echo   - Reiniciar: docker-compose restart
echo   - Status: docker-compose ps
echo ========================================
pause
