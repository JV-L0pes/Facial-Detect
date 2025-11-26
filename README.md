# Sistema de Reconhecimento Facial para Controle de Acesso

Sistema completo de reconhecimento facial com detecção de liveness para controle de acesso, desenvolvido em Python com FastAPI e interface web moderna com Next.js.

## 🚀 Características

- **Detecção Facial Avançada**: Utiliza RetinaFace via InsightFace para detecção precisa
- **Reconhecimento de Estado da Arte**: Embeddings ArcFace de 512 dimensões
- **Busca Vetorial Rápida**: Índice FAISS para busca eficiente de similaridade
- **Anti-Spoofing**: Detecção de liveness com análise de movimento e textura
- **Segurança**: Criptografia AES-256 para embeddings sensíveis
- **Interface Moderna**: Frontend Next.js com TypeScript e Tailwind CSS
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

### Frontend (Next.js 15)
- **Next.js 15**: Framework React com App Router
- **TypeScript**: Tipagem estática para maior segurança
- **Tailwind CSS**: Framework CSS utilitário
- **shadcn/ui**: Componentes UI modernos e acessíveis
- **TanStack Query**: Gerenciamento de estado servidor
- **Zustand**: Gerenciamento de estado cliente
- **Framer Motion**: Animações fluidas
- **React Hook Form + Zod**: Formulários com validação
- **Lucide React**: Ícones modernos
- **Sonner**: Notificações toast elegantes

### Segurança
- **AES-256**: Criptografia de embeddings
- **PyCryptodome**: Biblioteca de criptografia
- **Liveness Detection**: Anti-spoofing básico

## 📋 Pré-requisitos

- **Docker Desktop** (recomendado) OU ambiente de desenvolvimento local
- **Node.js 18+** (para desenvolvimento frontend)
- **Python 3.8+** (para ambiente venv) OU Miniconda/Anaconda (para ambiente conda)
- **CUDA Toolkit** (recomendado para GPU)
- **Webcam** para validação
- **Navegador moderno** com suporte a WebRTC

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
- Frontend: http://localhost (via Nginx)
- Frontend direto: http://localhost:3000 (Next.js)
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

## 🔧 Instalação Manual (Sem Docker)

### 📋 Pré-requisitos

- **Python 3.11** (recomendado) ou Python 3.12
- **Node.js 18+** instalado
- **CUDA Toolkit** (opcional, apenas se quiser usar GPU)

### 🚀 Guia Rápido - Rodar Localmente

#### Passo 1: Configurar o Backend (Python)

1. **Navegue até a pasta do projeto**
   ```bash
   cd Facial_Detect
   ```

2. **Crie e ative um ambiente virtual com Python 3.11**
   
   **Windows (PowerShell):**
   ```powershell
   # Usar Python 3.11 especificamente
   py -3.11 -m venv backend\.venv
   cd backend
   .\.venv\Scripts\Activate.ps1
   ```
   
   **Windows (CMD):**
   ```cmd
   py -3.11 -m venv backend\.venv
   cd backend
   .venv\Scripts\activate
   ```
   
   **Linux/Mac:**
   ```bash
   python3.11 -m venv backend/.venv
   cd backend
   source .venv/bin/activate
   ```

3. **Instale as dependências Python**
   ```bash
   # Atualizar pip primeiro
   python -m pip install --upgrade pip
   
   # Instalar dependências
   pip install -r requirements.txt
   ```
   
   **Nota sobre GPU vs CPU:**
   - **Com GPU:** O sistema detectará automaticamente e usará GPU se disponível
   - **Sem GPU ou forçar CPU:** O sistema funcionará normalmente em CPU (mais lento)
   - Para forçar CPU explicitamente:
     ```bash
     # Windows
     set DEVICE=cpu
     
     # Linux/Mac
     export DEVICE=cpu
     ```

4. **Execute o backend**
   
   **Opção 1: Usando Python diretamente (recomendado)**
   ```bash
   # Se estiver dentro de backend/
   python app/main.py
   
   # Se estiver na raiz do projeto
   python backend/app/main.py
   ```
   
   **Opção 2: Usando uvicorn**
   ```bash
   # Se estiver dentro de backend/
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   
   # Se estiver na raiz do projeto
   uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   
   O backend estará disponível em: **http://localhost:8000**
   - API Docs: http://localhost:8000/docs

#### Passo 2: Configurar o Frontend (Next.js)

1. **Abra um novo terminal** (mantenha o backend rodando)

2. **Navegue até a pasta frontend**
   ```bash
   cd frontend
   ```

3. **Instale as dependências**
   ```bash
   npm install
   ```

4. **Execute o frontend**
   ```bash
   npm run dev
   ```
   
   O frontend estará disponível em: **http://localhost:3000**

#### Passo 3: Acessar a Aplicação

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **Documentação API:** http://localhost:8000/docs

### 🔧 Opções Avançadas

#### Opção A: Com GPU (NVIDIA)

Se você tem GPU NVIDIA e quer melhor performance:

1. **Instale CUDA Toolkit** (se ainda não tiver)
   - Baixe de: https://developer.nvidia.com/cuda-downloads

2. **Instale PyTorch com suporte CUDA** (opcional, já está no requirements.txt)
   ```bash
   # O requirements.txt já inclui torch, mas se quiser versão específica:
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
   ```

3. **Instale FAISS GPU** (opcional, para melhor performance na busca)
   ```bash
   # Via conda (recomendado)
   conda install -c conda-forge faiss-gpu -y
   
   # Ou desinstale faiss-cpu e instale faiss-gpu
   pip uninstall faiss-cpu -y
   pip install faiss-gpu
   ```

4. **Execute o backend normalmente**
   - O sistema detectará automaticamente a GPU e usará CUDA

#### Opção B: Sem GPU (CPU Only)

O sistema funciona perfeitamente com CPU, apenas será mais lento:

1. **Instale as dependências normalmente**
   ```bash
   pip install -r backend/requirements.txt
   ```
   - O `requirements.txt` já inclui `faiss-cpu` que funciona em CPU
   - O sistema detectará automaticamente que não há GPU e usará CPU

2. **Para forçar CPU explicitamente** (opcional):
   ```bash
   # Windows
   set DEVICE=cpu
   
   # Linux/Mac
   export DEVICE=cpu
   ```

3. **Execute o backend normalmente**
   - O sistema funcionará em modo CPU automaticamente

### ⚠️ Notas Importantes

- **Python 3.11 recomendado:** Python 3.13 pode ter problemas com algumas dependências. Use Python 3.11 ou 3.12.
- **GPU vs CPU:** O sistema detecta automaticamente se há GPU disponível. Se não houver, usa CPU automaticamente. Funciona em ambos os modos.
- **Portas:** Certifique-se de que as portas 3000 (frontend) e 8000 (backend) estão livres.
- **CORS:** O backend está configurado para aceitar requisições do frontend em desenvolvimento.
- **Banco de Dados:** O SQLite será criado automaticamente em `data/database.db` na primeira execução.
- **Dependências:** O `requirements.txt` está configurado para funcionar tanto com GPU quanto CPU. Para GPU, você pode instalar `faiss-gpu` e `torch` com CUDA separadamente.

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
├── frontend/                    # Next.js Frontend
│   ├── src/
│   │   ├── app/                 # App Router pages
│   │   │   ├── layout.tsx       # Root layout
│   │   │   ├── page.tsx         # Home page
│   │   │   ├── cadastro/        # Register page
│   │   │   ├── validacao/       # Validation page
│   │   │   └── admin/           # Admin page
│   │   ├── components/          # React components
│   │   │   ├── ui/              # shadcn/ui components
│   │   │   ├── layout/          # Header, Footer
│   │   │   ├── home/            # Home components
│   │   │   ├── cadastro/        # Register components
│   │   │   ├── validacao/       # Validation components
│   │   │   └── admin/            # Admin components
│   │   ├── lib/                 # Utilities
│   │   │   ├── api/             # API clients
│   │   │   ├── hooks/           # Custom hooks
│   │   │   ├── store/           # Zustand store
│   │   │   └── utils/           # Helper functions
│   │   └── types/               # TypeScript types
│   ├── package.json             # Dependencies
│   ├── tailwind.config.ts       # Tailwind config
│   ├── next.config.js           # Next.js config
│   └── Dockerfile               # Frontend container
├── data/
│   ├── database.db             # SQLite
│   ├── faiss_index/            # Índices FAISS
│   └── logs/                   # Logs criptografados
├── config.py                   # Configurações
├── requirements.txt            # Dependências Python
└── docker-compose.yml          # Docker orchestration
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
