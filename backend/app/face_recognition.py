import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis
import faiss
import os
import pickle
from typing import List, Tuple, Optional
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import DEVICE, FACE_DETECTION_CONFIDENCE, FACE_RECOGNITION_THRESHOLD, EMBEDDING_DIMENSION, FAISS_INDEX_DIR, MODELS_DIR
from backend.app.encryption import encryption_manager

class FaceRecognitionSystem:
    def __init__(self):
        self.face_app = None
        self.faiss_index = None
        self.id_to_user = {}  # Mapear ID do FAISS para usuário
        self.next_faiss_id = 0
        self.load_models()
        self.load_faiss_index()
    
    def load_models(self):
        """Carrega modelos InsightFace"""
        try:
            # Forçar uso de GPU sempre que disponível
            if DEVICE == 'cuda':
                print("🚀 Configurando InsightFace para GPU...")
                self.face_app = FaceAnalysis(
                    name='buffalo_l',  # Modelo mais preciso
                    providers=['CUDAExecutionProvider', 'TensorrtExecutionProvider', 'CPUExecutionProvider']
                )
                # Usar tamanho máximo para melhor qualidade com GPU
                self.face_app.prepare(ctx_id=0, det_size=(1920, 1920))
                print("✅ Modelos InsightFace carregados com GPU!")
            else:
                print("⚠️ GPU não disponível, usando CPU...")
                self.face_app = FaceAnalysis(
                    name='buffalo_l',
                    providers=['CPUExecutionProvider']
                )
                self.face_app.prepare(ctx_id=-1, det_size=(1280, 1280))
                print("✅ Modelos InsightFace carregados com CPU!")

        except Exception as e:
            print(f"❌ Erro ao carregar modelos: {e}")
            raise
    
    def load_faiss_index(self):
        """Carrega ou cria índice FAISS"""
        index_path = FAISS_INDEX_DIR / "face_index.faiss"
        id_map_path = FAISS_INDEX_DIR / "id_mapping.pkl"
        
        if index_path.exists() and id_map_path.exists():
            try:
                # Carregar índice existente
                self.faiss_index = faiss.read_index(str(index_path))
                
                # Carregar mapeamento de IDs
                with open(id_map_path, 'rb') as f:
                    self.id_to_user = pickle.load(f)
                
                # Definir próximo ID disponível
                if self.id_to_user:
                    self.next_faiss_id = max(self.id_to_user.keys()) + 1
                else:
                    self.next_faiss_id = 0
                
                print(f"Índice FAISS carregado: {self.faiss_index.ntotal} embeddings")
                
            except Exception as e:
                print(f"Erro ao carregar índice FAISS: {e}")
                self._create_new_index()
        else:
            self._create_new_index()
    
    def _create_new_index(self):
        """Cria novo índice FAISS"""
        # Criar índice FlatIP (Inner Product) para similaridade de cosseno
        self.faiss_index = faiss.IndexFlatIP(EMBEDDING_DIMENSION)
        self.id_to_user = {}
        self.next_faiss_id = 0
        print("Novo índice FAISS criado")
    
    def save_faiss_index(self):
        """Salva índice FAISS e mapeamento"""
        try:
            # Salvar índice
            faiss.write_index(self.faiss_index, str(FAISS_INDEX_DIR / "face_index.faiss"))
            
            # Salvar mapeamento
            with open(FAISS_INDEX_DIR / "id_mapping.pkl", 'wb') as f:
                pickle.dump(self.id_to_user, f)
            
            print("Índice FAISS salvo com sucesso!")
            
        except Exception as e:
            print(f"Erro ao salvar índice FAISS: {e}")
    
    def detect_faces(self, image: np.ndarray) -> List[dict]:
        """Detecta faces na imagem"""
        try:
            faces = self.face_app.get(image)
            
            # Filtrar faces por confiança
            valid_faces = []
            for face in faces:
                if face.det_score >= FACE_DETECTION_CONFIDENCE:
                    valid_faces.append({
                        'bbox': face.bbox.astype(int),
                        'embedding': face.embedding,
                        'det_score': face.det_score,
                        'landmarks': face.kps if hasattr(face, 'kps') else None
                    })
            
            return valid_faces
            
        except Exception as e:
            print(f"Erro na detecção de faces: {e}")
            return []
    
    def extract_embedding(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Extrai embedding de uma face na imagem"""
        faces = self.detect_faces(image)
        
        if not faces:
            return None
        
        # Retornar embedding da face com maior confiança
        best_face = max(faces, key=lambda x: x['det_score'])
        return best_face['embedding']
    
    def add_user_embedding(self, embedding: np.ndarray, user_id: int) -> int:
        """Adiciona embedding de usuário ao índice FAISS"""
        try:
            # Normalizar embedding para similaridade de cosseno
            embedding_normalized = embedding / np.linalg.norm(embedding)
            
            # Adicionar ao índice FAISS
            faiss_id = self.next_faiss_id
            self.faiss_index.add(embedding_normalized.reshape(1, -1))
            
            # Mapear ID do FAISS para ID do usuário
            self.id_to_user[faiss_id] = user_id
            
            self.next_faiss_id += 1
            
            # Salvar índice atualizado
            self.save_faiss_index()
            
            return faiss_id
            
        except Exception as e:
            print(f"Erro ao adicionar embedding: {e}")
            raise
    
    def recognize_face(self, embedding: np.ndarray, k: int = 5) -> Tuple[Optional[int], float]:
        """Reconhece face comparando com embeddings conhecidos"""
        try:
            if self.faiss_index.ntotal == 0:
                return None, 1.0
            
            # Normalizar embedding
            embedding_normalized = embedding / np.linalg.norm(embedding)
            
            # Buscar k vizinhos mais próximos
            similarities, indices = self.faiss_index.search(
                embedding_normalized.reshape(1, -1), 
                min(k, self.faiss_index.ntotal)
            )
            
            # Pegar melhor resultado
            best_similarity = similarities[0][0]
            best_index = indices[0][0]
            
            # Converter similaridade para distância (1 - similaridade)
            distance = 1.0 - best_similarity
            
            # Verificar se está dentro do threshold
            if distance <= FACE_RECOGNITION_THRESHOLD:
                user_id = self.id_to_user.get(best_index)
                return user_id, distance
            else:
                return None, distance
                
        except Exception as e:
            print(f"Erro no reconhecimento: {e}")
            return None, 1.0
    
    def remove_user_embedding(self, faiss_id: int):
        """Remove embedding do usuário (implementação simplificada)"""
        # FAISS não suporta remoção eficiente, então marcamos como removido
        if faiss_id in self.id_to_user:
            del self.id_to_user[faiss_id]
            self.save_faiss_index()
    
    def clear_index(self):
        """Limpa completamente o índice FAISS"""
        try:
            # Criar novo índice vazio
            self._create_new_index()
            
            # Salvar índice limpo
            self.save_faiss_index()
            
            print("Índice FAISS limpo com sucesso!")
            
        except Exception as e:
            print(f"Erro ao limpar índice FAISS: {e}")
            raise
    
    def get_stats(self) -> dict:
        """Retorna estatísticas do sistema"""
        return {
            'total_embeddings': self.faiss_index.ntotal,
            'registered_users': len(self.id_to_user),
            'device': DEVICE,
            'threshold': FACE_RECOGNITION_THRESHOLD
        }

# Instância global do sistema de reconhecimento
face_recognition = FaceRecognitionSystem()
