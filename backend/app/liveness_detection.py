import cv2
import numpy as np
from typing import List, Tuple
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import LIVENESS_FRAMES_REQUIRED, MOVEMENT_THRESHOLD

class LivenessDetector:
    def __init__(self):
        self.frame_history = []
        self.max_history = 10  # Manter últimos 10 frames
    
    def add_frame(self, face_bbox: np.ndarray) -> bool:
        """Adiciona frame para análise de liveness"""
        # Normalizar bbox para análise consistente
        normalized_bbox = self._normalize_bbox(face_bbox)
        
        self.frame_history.append(normalized_bbox)
        
        # Manter apenas os últimos frames
        if len(self.frame_history) > self.max_history:
            self.frame_history.pop(0)
        
        # Verificar liveness se temos frames suficientes
        if len(self.frame_history) >= LIVENESS_FRAMES_REQUIRED:
            return self._analyze_movement()
        
        return False
    
    def _normalize_bbox(self, bbox: np.ndarray) -> np.ndarray:
        """Normaliza bbox para análise consistente"""
        # bbox formato: [x1, y1, x2, y2]
        x1, y1, x2, y2 = bbox
        
        # Calcular centro e dimensões
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        width = x2 - x1
        height = y2 - y1
        
        return np.array([center_x, center_y, width, height])
    
    def _analyze_movement(self) -> bool:
        """Analisa movimento entre frames para detectar liveness"""
        if len(self.frame_history) < LIVENESS_FRAMES_REQUIRED:
            return False
        
        # Calcular variação de posição do centro
        centers = np.array([frame[:2] for frame in self.frame_history[-LIVENESS_FRAMES_REQUIRED:]])
        
        # Calcular movimento total
        total_movement = 0
        for i in range(1, len(centers)):
            movement = np.linalg.norm(centers[i] - centers[i-1])
            total_movement += movement
        
        # Calcular movimento médio
        avg_movement = total_movement / (len(centers) - 1)
        
        # Verificar se movimento é suficiente
        return avg_movement >= MOVEMENT_THRESHOLD
    
    def reset(self):
        """Reseta histórico de frames"""
        self.frame_history = []
    
    def get_movement_stats(self) -> dict:
        """Retorna estatísticas de movimento"""
        if len(self.frame_history) < 2:
            return {"movement": 0, "frames_analyzed": len(self.frame_history)}
        
        centers = np.array([frame[:2] for frame in self.frame_history])
        
        # Calcular movimento total
        total_movement = 0
        for i in range(1, len(centers)):
            movement = np.linalg.norm(centers[i] - centers[i-1])
            total_movement += movement
        
        avg_movement = total_movement / (len(centers) - 1) if len(centers) > 1 else 0
        
        return {
            "movement": avg_movement,
            "frames_analyzed": len(self.frame_history),
            "liveness_passed": avg_movement >= MOVEMENT_THRESHOLD
        }

class AdvancedLivenessDetector:
    """Detector de liveness mais avançado usando análise de textura"""
    
    def __init__(self):
        self.frame_history = []
        self.texture_history = []
        self.max_history = 10
    
    def add_frame(self, face_image: np.ndarray, face_bbox: np.ndarray) -> bool:
        """Adiciona frame com análise de textura"""
        # Extrair região da face
        x1, y1, x2, y2 = face_bbox.astype(int)
        face_roi = face_image[y1:y2, x1:x2]
        
        if face_roi.size == 0:
            return False
        
        # Redimensionar para análise consistente
        face_resized = cv2.resize(face_roi, (64, 64))
        
        # Calcular características de textura (Laplacian variance)
        gray_face = cv2.cvtColor(face_resized, cv2.COLOR_BGR2GRAY)
        texture_score = cv2.Laplacian(gray_face, cv2.CV_64F).var()
        
        self.texture_history.append(texture_score)
        self.frame_history.append(self._normalize_bbox(face_bbox))
        
        # Manter histórico limitado
        if len(self.texture_history) > self.max_history:
            self.texture_history.pop(0)
            self.frame_history.pop(0)
        
        # Verificar liveness
        if len(self.texture_history) >= LIVENESS_FRAMES_REQUIRED:
            return self._analyze_texture_and_movement()
        
        return False
    
    def _normalize_bbox(self, bbox: np.ndarray) -> np.ndarray:
        """Normaliza bbox"""
        x1, y1, x2, y2 = bbox
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        width = x2 - x1
        height = y2 - y1
        return np.array([center_x, center_y, width, height])
    
    def _analyze_texture_and_movement(self) -> bool:
        """Analisa textura e movimento para liveness"""
        # Análise de movimento
        movement_passed = self._check_movement()
        
        # Análise de textura (variação indica pessoa real)
        texture_passed = self._check_texture_variation()
        
        # Ambos devem passar para considerar liveness
        return bool(movement_passed and texture_passed)
    
    def _check_movement(self) -> bool:
        """Verifica movimento entre frames"""
        if len(self.frame_history) < LIVENESS_FRAMES_REQUIRED:
            return False
        
        centers = np.array([frame[:2] for frame in self.frame_history[-LIVENESS_FRAMES_REQUIRED:]])
        
        total_movement = 0
        for i in range(1, len(centers)):
            movement = np.linalg.norm(centers[i] - centers[i-1])
            total_movement += movement
        
        avg_movement = total_movement / (len(centers) - 1)
        return bool(avg_movement >= MOVEMENT_THRESHOLD)
    
    def _check_texture_variation(self) -> bool:
        """Verifica variação de textura (indica pessoa real vs foto)"""
        if len(self.texture_history) < LIVENESS_FRAMES_REQUIRED:
            return False
        
        recent_textures = self.texture_history[-LIVENESS_FRAMES_REQUIRED:]
        
        # Calcular variação de textura
        texture_variance = np.var(recent_textures)
        
        # Threshold para variação mínima (fotos têm textura mais estável)
        min_texture_variance = 50.0
        
        return bool(texture_variance >= min_texture_variance)
    
    def reset(self):
        """Reseta histórico"""
        self.frame_history = []
        self.texture_history = []
    
    def get_stats(self) -> dict:
        """Retorna estatísticas detalhadas"""
        if len(self.texture_history) < 2:
            return {
                "movement": 0,
                "texture_variance": 0,
                "frames_analyzed": len(self.texture_history),
                "liveness_passed": False
            }
        
        # Estatísticas de movimento
        centers = np.array([frame[:2] for frame in self.frame_history])
        total_movement = 0
        for i in range(1, len(centers)):
            movement = np.linalg.norm(centers[i] - centers[i-1])
            total_movement += movement
        
        avg_movement = total_movement / (len(centers) - 1) if len(centers) > 1 else 0
        
        # Estatísticas de textura
        texture_variance = np.var(self.texture_history) if len(self.texture_history) > 1 else 0
        
        return {
            "movement": avg_movement,
            "texture_variance": texture_variance,
            "frames_analyzed": len(self.texture_history),
            "liveness_passed": avg_movement >= MOVEMENT_THRESHOLD and texture_variance >= 50.0
        }

# Instâncias globais dos detectores
liveness_detector = LivenessDetector()
advanced_liveness_detector = AdvancedLivenessDetector()
