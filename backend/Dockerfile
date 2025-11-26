# Dockerfile para o backend Python com GPU - OTIMIZADO
FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

# Evitar prompts interativos
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependências do sistema (cache layer)
RUN apt-get update && apt-get install -y \
    bash \
    ca-certificates \
    curl \
    wget \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Instalar Miniforge (cache layer)
RUN wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh -O /tmp/miniforge.sh && \
    bash /tmp/miniforge.sh -b -p /opt/miniconda && \
    rm /tmp/miniforge.sh

# Adicionar conda ao PATH
ENV PATH="/opt/miniconda/bin:${PATH}"

# Configurar conda (cache layer)
RUN conda config --system --remove-key channels || true && \
    conda config --system --add channels conda-forge && \
    conda config --system --set channel_priority strict

# Criar ambiente conda (cache layer)
RUN conda create -n faiss-gpu python=3.11 -y

# Instalar dependências pesadas (cache layer - só muda se requirements.txt mudar)
RUN /bin/bash -lc "source /opt/miniconda/bin/activate faiss-gpu && \
    conda install -c conda-forge faiss-gpu numpy=1.26.4 -y && \
    pip install --upgrade pip && \
    pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cu121"

# Definir diretório de trabalho
WORKDIR /app

# Copiar requirements.txt primeiro para cache de dependências
COPY backend/requirements.txt ./requirements.txt

# Instalar dependências Python restantes (cache layer)
# Nota: faiss-gpu e torch já estão instalados via conda/pip acima
# Filtrar faiss-cpu e torch do requirements.txt para evitar conflitos
RUN /bin/bash -lc "source /opt/miniconda/bin/activate faiss-gpu && \
    grep -v '^faiss-cpu' requirements.txt | grep -v '^torch' | grep -v '^torchvision' > requirements_docker.txt && \
    pip install -r requirements_docker.txt"

# Copiar código da aplicação (só esta parte vai rebuildar quando código mudar)
COPY backend/ ./
COPY config.py ./

# Criar diretórios necessários
RUN mkdir -p data/faiss_index data/logs

# Definir variáveis de ambiente
ENV PYTHONPATH=/app
ENV CUDA_VISIBLE_DEVICES=0

# Expor porta
EXPOSE 8000

# Script de inicialização
COPY backend/start_backend.sh /start_backend.sh
RUN chmod +x /start_backend.sh

# Comando padrão
CMD ["/start_backend.sh"]