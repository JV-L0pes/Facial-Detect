# Sistema de Reconhecimento Facial para Controle de Acesso

Sistema completo de reconhecimento facial com detecção de liveness para controle de acesso, desenvolvido em Python com FastAPI e interface web moderna.

## 🚀 Características

- **Detecção Facial Avançada**: Utiliza RetinaFace via InsightFace para detecção precisa
- **Reconhecimento de Estado da Arte**: Embeddings ArcFace de 512 dimensões
- **Busca Vetorial Rápida**: Índice FAISS para busca eficiente de similaridade
- **Anti-Spoofing**: Detecção de liveness com análise de movimento e textura
- **Segurança**: Criptografia AES-256 para embeddings sensíveis
- **Interface Moderna**: Frontend responsivo com design elegante
- **Compliance LGPD**: Não armazena fotos em claro, apenas embeddings criptografados
- **GPU Acelerado**: Suporte automático para CUDA (RTX/GTX)

## 🛠️ Tecnologias

### Backend
- **FastAPI**: Framework web moderno e rápido
- **InsightFace**: Biblioteca de reconhecimento facial
- **FAISS**: Busca vetorial eficiente
- **SQLAlchemy**: ORM para banco de dados
- **SQLite**: Banco de dados leve
- **OpenCV**: Processamento de imagens
- **PyTorch**: Deep learning com suporte GPU

### Frontend
- **HTML5/CSS3**: Interface moderna e responsiva
- **JavaScript**: Interatividade e WebRTC
- **Font Awesome**: Ícones elegantes
- **WebRTC**: Captura de webcam em tempo real

### Segurança
- **AES-256**: Criptografia de embeddings
- **PyCryptodome**: Biblioteca de criptografia
- **Liveness Detection**: Anti-spoofing básico

## 📋 Pré-requisitos

- Python 3.8+ (para ambiente venv) OU Miniconda/Anaconda (para ambiente conda)
- CUDA Toolkit (recomendado para GPU)
- Webcam para validação
- Navegador moderno com suporte a WebRTC

## 🐳 Instalação com Docker (Recomendado)

A forma mais fácil de executar o sistema é usando Docker. Isso garante que todas as dependências sejam instaladas corretamente.

### Pré-requisitos
- Docker Desktop instalado
- Docker Compose instalado
- NVIDIA Docker (opcional, para GPU)

### Instalação Rápida

1. **Clone o repositório**
```bash
git clone <url-do-repositorio>
cd Facial_Detect
```

2. **Execute o script de inicialização**

**Linux/Mac:**
```bash
chmod +x start_docker.sh
./start_docker.sh
```

**Windows:**
```cmd
start_docker.bat
```

3. **Acesse o sistema**
- Frontend: http://localhost
- Backend API: http://localhost:8000
- Documentação: http://localhost:8000/docs

### Comandos Docker Úteis

```bash
# Ver logs em tempo real
docker-compose logs -f

# Parar o sistema
docker-compose down

# Reiniciar serviços
docker-compose restart

# Ver status dos containers
docker-compose ps

# Reconstruir containers
docker-compose build --no-cache
```

## 🔧 Instalação Manual

### Opção 1: Ambiente Conda (Recomendado - 100% GPU)

Esta opção garante suporte completo à GPU com FAISS GPU e ONNX Runtime GPU.

1. **Clone o repositório**
```bash
git clone <repository-url>
cd Facial_Detect
```

2. **Instale Miniconda** (se não tiver)
- Baixe de: https://docs.conda.io/en/latest/miniconda.html
- Execute o instalador

3. **Crie e ative o ambiente conda**
```bash
# Criar ambiente com Python 3.11 (compatível com FAISS GPU)
conda create -n facial-detect python=3.11 -y

# Ativar ambiente
conda activate facial-detect

# Instalar FAISS GPU
conda install -c conda-forge faiss-gpu -y

# Instalar outras dependências
pip install -r requirements.txt
```

4. **Execute o sistema**
```bash
# Opção 1: Usar script automático (recomendado)
start_gpu.bat

# Opção 2: Manual
conda activate faiss-gpu
python backend/app/main.py
```

### Opção 2: Ambiente Virtual Python (CPU/GPU Limitado)

Esta opção usa FAISS CPU e pode ter limitações de GPU.

1. **Clone o repositório**
```bash
git clone <repository-url>
cd Facial_Detect
```

2. **Crie e ative ambiente virtual**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

3. **Instale dependências**
```bash
pip install -r requirements.txt
```

4. **Execute o sistema**
```bash
# Windows
venv\Scripts\activate
python backend/app/main.py

# Linux/Mac
source venv/bin/activate
python backend/app/main.py
```

### Acesse a aplicação
```
http://localhost:8000
```

## 📱 Como Usar

### 1. Cadastro de Usuários
- Acesse `/cadastro`
- Preencha nome e email
- Envie uma foto clara do rosto
- Sistema detecta automaticamente a face e extrai embedding

### 2. Validação de Acesso
- Acesse `/validacao`
- Clique em "Iniciar Câmera"
- Posicione seu rosto na câmera
- Sistema valida em tempo real com detecção de liveness

### 3. Painel Administrativo
- Acesse `/admin`
- Visualize estatísticas do sistema
- Gerencie usuários cadastrados
- Monitore logs de acesso

## ⚙️ Configuração

### Thresholds (config.py)
```python
FACE_DETECTION_CONFIDENCE = 0.25  # Confiança mínima para detecção
FACE_RECOGNITION_THRESHOLD = 0.25  # Distância máxima para reconhecimento
MOVEMENT_THRESHOLD = 0.1           # Movimento mínimo para liveness
```

### GPU
O sistema detecta automaticamente CUDA. Para forçar CPU:
```python
DEVICE = "cpu"  # Em config.py
```

## 🔒 Segurança

- **Embeddings Criptografados**: Todos os embeddings são criptografados com AES-256
- **Não Armazena Fotos**: Apenas embeddings matemáticos são salvos
- **Logs de Acesso**: Todas as tentativas são registradas
- **Anti-Spoofing**: Detecção de liveness previne ataques com fotos
- **LGPD Compliant**: Dados pessoais protegidos

## 📊 API Endpoints

### Cadastro
- `POST /api/register` - Cadastra novo usuário

### Validação
- `POST /api/validate` - Valida face em tempo real

### Administração
- `GET /api/users` - Lista usuários
- `GET /api/logs` - Lista logs de acesso
- `GET /api/stats` - Estatísticas do sistema
- `DELETE /api/users/{id}` - Remove usuário

## 🏗️ Arquitetura

```
Facial_Detect/
├── backend/
│   └── app/
│       ├── main.py              # FastAPI app
│       ├── models.py            # SQLAlchemy models
│       ├── database.py          # DB connection
│       ├── face_recognition.py  # Core facial recognition
│       ├── liveness_detection.py # Anti-spoofing
│       └── encryption.py        # Crypto utils
├── frontend/
│   ├── index.html               # Página principal
│   ├── cadastro.html           # Cadastro de usuários
│   ├── validacao.html          # Validação facial
│   ├── admin.html              # Painel administrativo
│   └── css/
│       └── styles.css          # Estilos
├── data/
│   ├── database.db             # SQLite
│   ├── faiss_index/            # Índices FAISS
│   └── logs/                   # Logs criptografados
├── config.py                   # Configurações
└── requirements.txt            # Dependências
```

## 🔄 Fluxo de Funcionamento

### Cadastro
1. Usuário envia foto
2. Sistema detecta face com RetinaFace
3. Extrai embedding (512-dim) com ArcFace
4. Criptografa embedding
5. Salva no banco e adiciona ao índice FAISS

### Validação
1. Captura vídeo via WebRTC
2. Detecta face em tempo real
3. Verifica liveness (movimento + textura)
4. Extrai embedding da face
5. Busca similaridade no FAISS
6. Se distância < threshold → acesso liberado
7. Registra tentativa no log

## 🐛 Troubleshooting

### Problemas Comuns

**Erro de CUDA/GPU**
```bash
# Verificar se CUDA está disponível
python -c "import torch; print(torch.cuda.is_available())"

# Verificar ONNX Runtime GPU
python -c "import onnxruntime as ort; print(ort.get_available_providers())"

# Verificar FAISS GPU
python -c "import faiss; print(hasattr(faiss, 'StandardGpuResources'))"
```

**Erro "cublasLt64_12.dll missing"**
- Instale CUDA Toolkit do site oficial da NVIDIA
- Adicione o diretório bin do CUDA ao PATH do sistema
- Use o ambiente conda (Opção 1) que instala CUDA automaticamente

**Erro de NumPy incompatível**
```bash
# No ambiente conda
conda install "numpy<2" -y

# No ambiente venv
pip install "numpy<2"
```

**FAISS GPU não funciona**
- Use o ambiente conda (Opção 1) que instala FAISS GPU corretamente
- Verifique se tem CUDA Toolkit instalado
- Para Windows, o ambiente conda é mais confiável

**Câmera não funciona**
- Verificar permissões do navegador
- Usar HTTPS em produção
- Testar em navegador diferente

**Baixa precisão**
- Ajustar thresholds em config.py
- Usar fotos de melhor qualidade
- Verificar iluminação

### Verificação do Ambiente

**Para ambiente Conda:**
```bash
conda activate facial-detect
python -c "
import faiss
import onnxruntime as ort
import torch
print('FAISS GPU:', hasattr(faiss, 'StandardGpuResources'))
print('ONNX GPU:', 'CUDAExecutionProvider' in ort.get_available_providers())
print('PyTorch CUDA:', torch.cuda.is_available())
"
```

**Para ambiente venv:**
```bash
# Windows
venv\Scripts\activate
python -c "
import faiss
import onnxruntime as ort
import torch
print('FAISS CPU:', not hasattr(faiss, 'StandardGpuResources'))
print('ONNX GPU:', 'CUDAExecutionProvider' in ort.get_available_providers())
print('PyTorch CUDA:', torch.cuda.is_available())
"
```

### Logs
```bash
# Verificar logs do sistema
tail -f data/logs/system.log
```

## 📈 Performance

- **Detecção**: ~50ms por frame (GPU)
- **Reconhecimento**: ~10ms por embedding
- **Busca FAISS**: ~1ms para 1000 usuários
- **Liveness**: ~20ms por análise

## 🔮 Próximas Melhorias

- [ ] Suporte a múltiplas faces
- [ ] Detecção de máscaras
- [ ] Integração com hardware (GPIO/MQTT)
- [ ] API REST completa
- [ ] Docker containerization
- [ ] Testes automatizados
- [ ] Dashboard em tempo real
