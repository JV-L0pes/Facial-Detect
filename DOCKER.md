# 🐳 Docker Setup - Sistema de Reconhecimento Facial

## Instalação Rápida

### 1. Pré-requisitos
- Docker Desktop instalado
- Docker Compose instalado
- NVIDIA Docker (opcional, para GPU)

### 2. Executar o Sistema

**Linux/Mac:**
```bash
chmod +x start_docker.sh
./start_docker.sh
```

**Windows:**
```cmd
start_docker.bat
```

### 3. Acessar o Sistema
- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs

## Comandos Úteis

### Gerenciamento de Containers
```bash
# Ver logs em tempo real
docker-compose logs -f

# Ver logs de um serviço específico
docker-compose logs -f backend
docker-compose logs -f frontend

# Parar o sistema
docker-compose down

# Reiniciar serviços
docker-compose restart

# Reiniciar apenas o backend
docker-compose restart backend

# Ver status dos containers
docker-compose ps
```

### Build e Desenvolvimento
```bash
# Reconstruir containers (após mudanças no código)
docker-compose build --no-cache

# Reconstruir apenas o backend
docker-compose build --no-cache backend

# Executar comando dentro do container
docker-compose exec backend bash
docker-compose exec frontend sh
```

### Monitoramento
```bash
# Ver uso de recursos
docker stats

# Ver informações detalhadas dos containers
docker-compose ps -a
docker inspect facial-detect-backend
docker inspect facial-detect-frontend
```

## Estrutura dos Containers

### Backend Container
- **Imagem**: Ubuntu 22.04 + CUDA 12.1
- **Python**: 3.11 com ambiente conda
- **GPU**: Suporte NVIDIA CUDA
- **Porta**: 8000
- **Volumes**: `./data:/app/data`, `./logs:/app/logs`

### Frontend Container
- **Imagem**: Nginx Alpine
- **Porta**: 80
- **Proxy**: Redireciona `/api/` para backend

## Troubleshooting

### Problemas Comuns

1. **GPU não detectada**
   ```bash
   # Verificar se NVIDIA Docker está instalado
   docker run --rm --gpus all nvidia/cuda:12.1-base-ubuntu22.04 nvidia-smi
   ```

2. **Porta já em uso**
   ```bash
   # Verificar portas em uso
   netstat -tulpn | grep :80
   netstat -tulpn | grep :8000
   
   # Parar containers conflitantes
   docker-compose down
   ```

3. **Erro de permissão**
   ```bash
   # Linux: Dar permissão aos scripts
   chmod +x start_docker.sh
   chmod +x docker/start_backend.sh
   ```

4. **Container não inicia**
   ```bash
   # Ver logs detalhados
   docker-compose logs backend
   docker-compose logs frontend
   
   # Verificar saúde dos containers
   docker-compose ps
   ```

### Limpeza

```bash
# Parar e remover containers
docker-compose down

# Remover volumes (CUIDADO: apaga dados)
docker-compose down -v

# Limpar imagens não utilizadas
docker system prune -a

# Limpar tudo (CUIDADO: apaga tudo)
docker system prune -a --volumes
```

## Configuração Avançada

### Variáveis de Ambiente
Edite o arquivo `.env.docker` para personalizar:
- Thresholds de detecção
- Configurações de GPU
- Configurações de banco de dados
- Configurações de log

### Volumes Persistentes
Os dados são salvos em:
- `./data/` - Banco de dados e índices FAISS
- `./logs/` - Logs da aplicação

### Rede
Os containers se comunicam através da rede `facial-detect-network`.

## Performance

### GPU
- O sistema usa CUDA 12.1 para aceleração GPU
- FAISS GPU para busca vetorial rápida
- ONNX Runtime GPU para inferência

### CPU Fallback
Se GPU não estiver disponível, o sistema funciona com CPU (mais lento).

### Monitoramento
```bash
# Ver uso de GPU
nvidia-smi

# Ver uso de CPU/RAM
docker stats facial-detect-backend
```
