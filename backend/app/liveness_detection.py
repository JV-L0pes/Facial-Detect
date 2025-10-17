import cv2
import numpy as np
from typing import List, Tuple
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import (
    LIVENESS_FRAMES_REQUIRED, MOVEMENT_THRESHOLD, 
    TEXTURE_VARIANCE_THRESHOLD, BLINK_DETECTION_ENABLED, 
    EYE_ASPECT_RATIO_THRESHOLD
)

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
    """Detector de liveness mais avançado usando análise de textura e detecção de piscadas"""
    
    def __init__(self):
        self.frame_history = []
        self.texture_history = []
        self.eye_aspect_ratios = []
        self.blink_count = 0
        self.max_history = 10
        self.blink_threshold = EYE_ASPECT_RATIO_THRESHOLD
        self.consecutive_frames = 0
        self.blink_detected = False
    
    def add_frame(self, face_image: np.ndarray, face_bbox: np.ndarray, landmarks: np.ndarray = None) -> bool:
        """Adiciona frame com análise de textura e detecção de piscadas"""
        print(f"DEBUG LIVENESS: Adicionando frame - Histórico atual: {len(self.frame_history)}")
        
        # Extrair região da face
        x1, y1, x2, y2 = face_bbox.astype(int)
        face_roi = face_image[y1:y2, x1:x2]
        
        if face_roi.size == 0:
            print("DEBUG LIVENESS: ROI vazio")
            return False
        
        # Redimensionar para análise consistente
        face_resized = cv2.resize(face_roi, (64, 64))
        
        # Calcular características de textura (Laplacian variance)
        gray_face = cv2.cvtColor(face_resized, cv2.COLOR_BGR2GRAY)
        texture_score = cv2.Laplacian(gray_face, cv2.CV_64F).var()
        
        self.texture_history.append(texture_score)
        self.frame_history.append(self._normalize_bbox(face_bbox))
        
        print(f"DEBUG LIVENESS: Textura score: {texture_score:.2f}")
        
        # Detecção de piscadas (se landmarks disponíveis)
        if BLINK_DETECTION_ENABLED and landmarks is not None:
            ear = self._calculate_eye_aspect_ratio(landmarks)
            self.eye_aspect_ratios.append(ear)
            
            # Detectar piscada
            if len(self.eye_aspect_ratios) >= 3:
                self._detect_blink()
        
        # Manter histórico limitado
        if len(self.texture_history) > self.max_history:
            self.texture_history.pop(0)
            self.frame_history.pop(0)
        
        if len(self.eye_aspect_ratios) > self.max_history:
            self.eye_aspect_ratios.pop(0)
        
        # Verificar liveness
        if len(self.texture_history) >= LIVENESS_FRAMES_REQUIRED:
            print(f"DEBUG LIVENESS: Analisando liveness com {len(self.texture_history)} frames")
            result = self._analyze_texture_and_movement()
            print(f"DEBUG LIVENESS: Resultado da análise: {result}")
            return result
        
        print(f"DEBUG LIVENESS: Frames insuficientes ({len(self.texture_history)} < {LIVENESS_FRAMES_REQUIRED})")
        return False
    
    def _detect_blink(self):
        """Detecta piscadas baseado no Eye Aspect Ratio"""
        try:
            if len(self.eye_aspect_ratios) < 3:
                return
            
            # Verificar se há uma queda significativa no EAR (piscada)
            current_ear = self.eye_aspect_ratios[-1]
            previous_ear = self.eye_aspect_ratios[-2]
            
            # Se EAR caiu abaixo do threshold, considerar como piscada
            if current_ear < self.blink_threshold and previous_ear >= self.blink_threshold:
                self.blink_count += 1
                self.blink_detected = True
                print(f"Piscada detectada! Total: {self.blink_count}")
                
        except Exception as e:
            print(f"Erro na detecção de piscada: {e}")
    
    def _normalize_bbox(self, bbox: np.ndarray) -> np.ndarray:
        """Normaliza bbox"""
        x1, y1, x2, y2 = bbox
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        width = x2 - x1
        height = y2 - y1
        return np.array([center_x, center_y, width, height])
    
    def _analyze_texture_and_movement(self) -> bool:
        """Analisa textura, movimento e piscadas para liveness"""
        # Análise de movimento
        movement_passed = self._check_movement()
        
        # Análise de textura (variação indica pessoa real)
        texture_passed = self._check_texture_variation()
        
        # Análise de piscadas (se habilitada)
        blink_passed = True
        if BLINK_DETECTION_ENABLED:
            blink_passed = self._check_blink_detection()
        
        # Pelo menos movimento e textura devem passar
        # Piscada é opcional mas melhora a precisão
        return bool(movement_passed and texture_passed and blink_passed)
    
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
        
        # Usar threshold configurável
        return bool(texture_variance >= TEXTURE_VARIANCE_THRESHOLD)
    
    def _check_blink_detection(self) -> bool:
        """Verifica se houve pelo menos uma piscada detectada"""
        # Se não temos dados suficientes, considerar como passou
        if len(self.eye_aspect_ratios) < LIVENESS_FRAMES_REQUIRED:
            return True
        
        # Se já detectamos uma piscada, sempre passar
        if self.blink_count > 0:
            return True
        
        # Se temos dados suficientes mas não detectamos piscada, falhar
        return False
    
    def _calculate_eye_aspect_ratio(self, landmarks: np.ndarray) -> float:
        """Calcula Eye Aspect Ratio para detecção de piscadas"""
        try:
            if landmarks is None or len(landmarks) < 6:
                return 0.0
            
            # Pontos dos olhos (formato InsightFace)
            # Olho esquerdo: pontos 0, 1, 2, 3, 4, 5
            # Olho direito: pontos 6, 7, 8, 9, 10, 11
            
            # Olho esquerdo
            left_eye_points = landmarks[0:6]
            left_ear = self._calculate_ear(left_eye_points)
            
            # Olho direito
            right_eye_points = landmarks[6:12]
            right_ear = self._calculate_ear(right_eye_points)
            
            # EAR médio
            ear = (left_ear + right_ear) / 2.0
            
            return ear
            
        except Exception as e:
            print(f"Erro no cálculo de EAR: {e}")
            return 0.0
    
    def _calculate_ear(self, eye_points: np.ndarray) -> float:
        """Calcula Eye Aspect Ratio para um olho"""
        try:
            if len(eye_points) < 6:
                return 0.0
            
            # Calcular distâncias verticais
            A = np.linalg.norm(eye_points[1] - eye_points[5])
            B = np.linalg.norm(eye_points[2] - eye_points[4])
            
            # Calcular distância horizontal
            C = np.linalg.norm(eye_points[0] - eye_points[3])
            
            # EAR = (A + B) / (2 * C)
            ear = (A + B) / (2.0 * C)
            
            return ear
            
        except Exception as e:
            print(f"Erro no cálculo de EAR individual: {e}")
            return 0.0
    
    def reset(self):
        """Reseta histórico"""
        self.frame_history = []
        self.texture_history = []
        self.eye_aspect_ratios = []
        self.blink_count = 0
        self.blink_detected = False
        self.consecutive_frames = 0
    
    def get_stats(self) -> dict:
        """Retorna estatísticas detalhadas"""
        if len(self.texture_history) < 2:
            return {
                "movement": 0,
                "texture_variance": 0,
                "blink_count": self.blink_count,
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
        
        # Verificar se liveness passou
        movement_passed = avg_movement >= MOVEMENT_THRESHOLD
        texture_passed = texture_variance >= TEXTURE_VARIANCE_THRESHOLD
        blink_passed = True
        if BLINK_DETECTION_ENABLED:
            blink_passed = self.blink_count > 0 or len(self.eye_aspect_ratios) < LIVENESS_FRAMES_REQUIRED
        
        liveness_passed = movement_passed and texture_passed and blink_passed
        
        return {
            "movement": avg_movement,
            "texture_variance": texture_variance,
            "blink_count": self.blink_count,
            "frames_analyzed": len(self.texture_history),
            "liveness_passed": liveness_passed,
            "movement_passed": movement_passed,
            "texture_passed": texture_passed,
            "blink_passed": blink_passed
        }

# Instâncias globais dos detectores
liveness_detector = LivenessDetector()
advanced_liveness_detector = AdvancedLivenessDetector()
