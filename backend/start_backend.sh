#!/bin/bash

echo "========================================"
echo "Sistema de Reconhecimento Facial"
echo "========================================"
echo "Iniciando backend..."

# Ativar ambiente conda
source /opt/miniconda/bin/activate faiss-gpu

# Verificar GPU
echo "Verificando GPU..."
python -c "import torch; print(f'CUDA disponível: {torch.cuda.is_available()}')"

# Verificar dependências
echo "Verificando dependências..."
python -c "import faiss; print(f'FAISS GPU: {hasattr(faiss, \"StandardGpuResources\")}')"
python -c "import onnxruntime as ort; print(f'ONNX GPU: {\"CUDAExecutionProvider\" in ort.get_available_providers()}')"

# Inicializar banco de dados
echo "Inicializando banco de dados..."
python -c "from app.database import init_database; init_database()"

# Iniciar servidor
echo "Iniciando servidor FastAPI..."
echo "Backend disponível em: http://localhost:8000"
echo "API Docs em: http://localhost:8000/docs"
echo "========================================"

# Executar aplicação
cd /app
python app/main.py
