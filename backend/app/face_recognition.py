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
from config import (
    DEVICE, FACE_DETECTION_CONFIDENCE, FACE_RECOGNITION_THRESHOLD, 
    EMBEDDING_DIMENSION, FAISS_INDEX_DIR, MODELS_DIR,
    FACE_DETECTION_CONFIDENCE_HIGH, FACE_RECOGNITION_THRESHOLD_STRICT,
    FACE_RECOGNITION_THRESHOLD_RELAXED, MIN_FACE_SIZE, MAX_FACE_SIZE
)
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
        """Carrega modelos InsightFace - 100% GPU ONLY"""
        try:
            if DEVICE != 'cuda':
                raise RuntimeError("GPU não disponível! Sistema configurado para 100% GPU ONLY.")
            
            print("Configurando InsightFace para 100% GPU ONLY...")
            
            # Verificar se CUDA está realmente disponível
            import torch
            if not torch.cuda.is_available():
                raise RuntimeError("CUDA não está disponível no PyTorch!")
            
            # Configurar InsightFace com APENAS CUDA
            self.face_app = FaceAnalysis(
                name='buffalo_l',  # Modelo mais preciso
                providers=['CUDAExecutionProvider']  # 100% GPU, ZERO fallback
            )
            
            # Preparar com configurações GPU otimizadas
            self.face_app.prepare(ctx_id=0, det_size=(1920, 1920))
            
            # Verificar se realmente está usando GPU
            providers = self.face_app.models['detection'].session.get_providers()
            if 'CUDAExecutionProvider' not in providers:
                raise RuntimeError("Falha ao configurar GPU! Usando CPU como fallback.")
            
            print("Modelos InsightFace carregados com 100% GPU ONLY!")
            print(f"Providers ativos: {providers}")

        except Exception as e:
            print(f"Erro ao carregar modelos: {e}")
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
    
    def detect_faces(self, image: np.ndarray, high_precision: bool = False) -> List[dict]:
        """Detecta faces na imagem com opção de alta precisão"""
        try:
            faces = self.face_app.get(image)
            
            # Escolher threshold baseado na precisão desejada
            confidence_threshold = FACE_DETECTION_CONFIDENCE_HIGH if high_precision else FACE_DETECTION_CONFIDENCE
            
            # Filtrar faces por confiança e qualidade
            valid_faces = []
            for face in faces:
                if face.det_score >= confidence_threshold:
                    # Verificar qualidade da face detectada
                    if self._is_face_quality_good(face, image):
                        valid_faces.append({
                            'bbox': face.bbox.astype(int),
                            'embedding': face.embedding,
                            'det_score': face.det_score,
                            'landmarks': face.kps if hasattr(face, 'kps') else None,
                            'quality_score': self._calculate_face_quality(face, image)
                        })
            
            # Ordenar por qualidade combinada (det_score + quality_score)
            valid_faces.sort(key=lambda x: x['det_score'] * x['quality_score'], reverse=True)
            
            return valid_faces
            
        except Exception as e:
            print(f"Erro na detecção de faces: {e}")
            return []
    
    def _is_face_quality_good(self, face, image: np.ndarray) -> bool:
        """Verifica se a qualidade da face detectada é adequada"""
        try:
            bbox = face.bbox.astype(int)
            x1, y1, x2, y2 = bbox
            
            # Verificar tamanho da face
            face_width = x2 - x1
            face_height = y2 - y1
            
            if face_width < MIN_FACE_SIZE or face_height < MIN_FACE_SIZE:
                return False
            
            if face_width > MAX_FACE_SIZE or face_height > MAX_FACE_SIZE:
                return False
            
            # Verificar se a face está dentro dos limites da imagem
            img_height, img_width = image.shape[:2]
            if x1 < 0 or y1 < 0 or x2 > img_width or y2 > img_height:
                return False
            
            # Verificar proporção da face (não muito alongada)
            aspect_ratio = face_width / face_height
            if aspect_ratio < 0.5 or aspect_ratio > 2.0:
                return False
            
            return True
            
        except Exception as e:
            print(f"Erro na verificação de qualidade: {e}")
            return False
    
    def _calculate_face_quality(self, face, image: np.ndarray) -> float:
        """Calcula score de qualidade da face"""
        try:
            bbox = face.bbox.astype(int)
            x1, y1, x2, y2 = bbox
            
            # Extrair região da face
            face_roi = image[y1:y2, x1:x2]
            
            if face_roi.size == 0:
                return 0.0
            
            # Converter para escala de cinza
            gray_face = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
            
            # Calcular nitidez usando Laplacian
            laplacian_var = cv2.Laplacian(gray_face, cv2.CV_64F).var()
            
            # Calcular brilho médio
            brightness = np.mean(gray_face)
            
            # Calcular contraste
            contrast = np.std(gray_face)
            
            # Normalizar scores (valores empíricos)
            sharpness_score = min(laplacian_var / 1000.0, 1.0)  # Normalizar para 0-1
            brightness_score = 1.0 - abs(brightness - 128) / 128.0  # Ideal é 128
            contrast_score = min(contrast / 64.0, 1.0)  # Normalizar para 0-1
            
            # Score combinado
            quality_score = (sharpness_score * 0.4 + brightness_score * 0.3 + contrast_score * 0.3)
            
            return max(0.0, min(1.0, quality_score))
            
        except Exception as e:
            print(f"Erro no cálculo de qualidade: {e}")
            return 0.0
    
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
    
    def recognize_face(self, embedding: np.ndarray, k: int = 5, adaptive_threshold: bool = True) -> Tuple[Optional[int], float]:
        """Reconhece face comparando com embeddings conhecidos com threshold adaptativo"""
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
            
            # Threshold adaptativo baseado na qualidade dos resultados
            if adaptive_threshold:
                threshold = self._get_adaptive_threshold(similarities[0])
            else:
                threshold = FACE_RECOGNITION_THRESHOLD
            
            # Verificar se está dentro do threshold
            if distance <= threshold:
                user_id = self.id_to_user.get(best_index)
                return user_id, distance
            else:
                return None, distance
                
        except Exception as e:
            print(f"Erro no reconhecimento: {e}")
            return None, 1.0
    
    def _get_adaptive_threshold(self, similarities: np.ndarray) -> float:
        """Calcula threshold adaptativo baseado na distribuição de similaridades"""
        try:
            if len(similarities) < 2:
                return FACE_RECOGNITION_THRESHOLD
            
            # Calcular diferença entre melhor e segundo melhor resultado
            best_sim = similarities[0]
            second_best_sim = similarities[1] if len(similarities) > 1 else best_sim
            
            gap = best_sim - second_best_sim
            
            # Se há uma grande diferença, usar threshold mais relaxado
            if gap > 0.1:  # Diferença significativa
                return FACE_RECOGNITION_THRESHOLD_RELAXED
            # Se há pouca diferença, usar threshold mais rigoroso
            elif gap < 0.05:  # Diferença pequena
                return FACE_RECOGNITION_THRESHOLD_STRICT
            else:
                return FACE_RECOGNITION_THRESHOLD
                
        except Exception as e:
            print(f"Erro no cálculo de threshold adaptativo: {e}")
            return FACE_RECOGNITION_THRESHOLD
    
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
