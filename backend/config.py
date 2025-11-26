import os
import torch
from pathlib import Path

# Configurações do projeto
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
LOGS_DIR = DATA_DIR / "logs"
FAISS_INDEX_DIR = DATA_DIR / "faiss_index"

# Criar diretórios se não existirem
DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
FAISS_INDEX_DIR.mkdir(exist_ok=True)

# Configurações de GPU
# Para forçar CPU, defina: DEVICE = "cpu"
# Para usar GPU (se disponível), defina: DEVICE = "cuda" ou deixe automático
DEVICE = os.getenv("DEVICE", "cuda" if torch.cuda.is_available() else "cpu")

if DEVICE == "cuda":
    if not torch.cuda.is_available():
        print("⚠️  AVISO: CUDA solicitado mas não disponível. Usando CPU.")
        DEVICE = "cpu"
    else:
        # Verificar se CUDA está realmente funcionando
        try:
            test_tensor = torch.tensor([1.0]).cuda()
            print(f"✅ Usando dispositivo: {DEVICE} (GPU)")
        except Exception as e:
            print(f"⚠️  AVISO: CUDA não está funcionando: {e}. Usando CPU.")
            DEVICE = "cpu"
else:
    print(f"✅ Usando dispositivo: {DEVICE} (CPU)")

# Configurações de reconhecimento facial
FACE_DETECTION_CONFIDENCE = 0.25  # Threshold de confiança para detecção
FACE_RECOGNITION_THRESHOLD = (
    0.4  # Threshold para reconhecimento (distância máxima) - Relaxado para teste
)
EMBEDDING_DIMENSION = 512  # Dimensão dos embeddings ArcFace

# Configurações avançadas de precisão
FACE_DETECTION_CONFIDENCE_HIGH = 0.4  # Threshold mais rigoroso para casos críticos
FACE_RECOGNITION_THRESHOLD_STRICT = 0.2  # Threshold mais rigoroso para alta segurança
FACE_RECOGNITION_THRESHOLD_RELAXED = 0.35  # Threshold mais relaxado para casos difíceis
MIN_FACE_SIZE = 80  # Tamanho mínimo da face em pixels
MAX_FACE_SIZE = 2000  # Tamanho máximo da face em pixels

# Configurações de segurança
ENCRYPTION_KEY = os.getenv(
    "ENCRYPTION_KEY", "facial_detect_demo_key_2024"
)  # Em produção, usar variável de ambiente
AES_KEY_LENGTH = 32  # 256 bits

# Configurações do banco de dados
DATABASE_URL = f"sqlite:///{DATA_DIR}/database.db"

# Configurações da API
API_HOST = "0.0.0.0"
API_PORT = 8000
API_TITLE = "Sistema Reconhecimento Facial"
API_VERSION = "1.0.0"

# Configurações de upload
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}

# Configurações de liveness detection
LIVENESS_FRAMES_REQUIRED = 3  # Número mínimo de frames para análise
MOVEMENT_THRESHOLD = 0.1  # Threshold mínimo de movimento para liveness
TEXTURE_VARIANCE_THRESHOLD = 50.0  # Threshold para variação de textura
BLINK_DETECTION_ENABLED = True  # Detectar piscadas para liveness
EYE_ASPECT_RATIO_THRESHOLD = 0.25  # Threshold para detecção de piscada
