#!/bin/bash
set -e

# Verificar se conda está instalado
if [ -f "/opt/miniconda/bin/activate" ]; then
    echo "📦 Ativando ambiente conda..."
    source /opt/miniconda/bin/activate facial-detect
else
    echo "⚠️  Conda não encontrado em /opt/miniconda/bin/activate"
    echo "   Tentando usar Python do sistema..."
    # Verificar se python está disponível
    if ! command -v python &> /dev/null; then
        echo "❌ Python não encontrado! Por favor, instale Python ou use Docker."
        exit 1
    fi
fi

# Verificar GPU/CUDA
echo "🔍 Verificando disponibilidade de GPU..."
python -c "
try:
    import torch
    if torch.cuda.is_available():
        print(f'✅ GPU detectada: {torch.cuda.get_device_name(0)}')
        print(f'   CUDA Version: {torch.version.cuda}')
        print(f'   GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB')
        print('   Modo: GPU (CUDA)')
    else:
        print('💻 GPU não detectada')
        print('   Modo: CPU Only')
        print('   O sistema funcionará normalmente em CPU')
except ImportError:
    print('💻 PyTorch não instalado')
    print('   Modo: CPU Only')
    print('   O sistema funcionará normalmente em CPU')
"

# Inicializar banco de dados
echo "🔄 Inicializando banco de dados..."
python -c "from app.database import init_database; init_database()"

# Iniciar servidor FastAPI
echo "🚀 Iniciando servidor FastAPI na porta 8000..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000

