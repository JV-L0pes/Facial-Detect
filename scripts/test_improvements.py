#!/usr/bin/env python3
"""
Script para testar as melhorias implementadas no sistema de reconhecimento facial
"""

import sys
import os
import cv2
import numpy as np
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

from backend.app.face_recognition import face_recognition
from backend.app.liveness_detection import advanced_liveness_detector
from config import *

def test_face_quality_detection():
    """Testa a detecção de qualidade de faces"""
    print("Testando detecção de qualidade de faces...")
    
    # Criar imagem de teste com face simulada
    test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    # Adicionar uma face simulada na imagem
    cv2.rectangle(test_image, (200, 150), (400, 350), (128, 128, 128), -1)
    cv2.circle(test_image, (250, 200), 20, (0, 0, 0), -1)  # Olho esquerdo
    cv2.circle(test_image, (350, 200), 20, (0, 0, 0), -1)  # Olho direito
    cv2.ellipse(test_image, (300, 280), (30, 15), 0, 0, 180, (0, 0, 0), -1)  # Boca
    
    # Testar detecção normal
    faces_normal = face_recognition.detect_faces(test_image, high_precision=False)
    print(f"   Detecção normal: {len(faces_normal)} faces")
    
    # Testar detecção de alta precisão
    faces_high = face_recognition.detect_faces(test_image, high_precision=True)
    print(f"   Detecção alta precisão: {len(faces_high)} faces")
    
    return len(faces_normal), len(faces_high)

def test_adaptive_threshold():
    """Testa o threshold adaptativo"""
    print("Testando threshold adaptativo...")
    
    # Criar embedding de teste
    test_embedding = np.random.randn(512).astype(np.float32)
    
    # Testar reconhecimento com threshold adaptativo
    user_id, distance = face_recognition.recognize_face(test_embedding, adaptive_threshold=True)
    print(f"   Reconhecimento adaptativo: user_id={user_id}, distance={distance:.3f}")
    
    # Testar reconhecimento com threshold fixo
    user_id_fixed, distance_fixed = face_recognition.recognize_face(test_embedding, adaptive_threshold=False)
    print(f"   Reconhecimento fixo: user_id={user_id_fixed}, distance={distance_fixed:.3f}")
    
    return distance, distance_fixed

def test_liveness_detection():
    """Testa a detecção de liveness melhorada"""
    print("Testando detecção de liveness...")
    
    # Criar frames de teste simulando movimento
    frames = []
    for i in range(5):
        # Simular movimento da face
        x_offset = i * 10
        y_offset = i * 5
        
        # Criar bbox simulando movimento
        bbox = np.array([100 + x_offset, 100 + y_offset, 200 + x_offset, 200 + y_offset])
        
        # Criar imagem de teste
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Simular landmarks dos olhos
        landmarks = np.random.randn(12, 2) * 50 + 150
        
        # Adicionar frame ao detector
        liveness_passed = advanced_liveness_detector.add_frame(test_image, bbox, landmarks)
        
        frames.append({
            'bbox': bbox,
            'liveness_passed': liveness_passed,
            'frame': i
        })
    
    # Obter estatísticas
    stats = advanced_liveness_detector.get_stats()
    print(f"   Estatísticas: {stats}")
    
    return stats

def test_configuration_values():
    """Testa os novos valores de configuração"""
    print("Testando configurações...")
    
    configs = {
        'FACE_DETECTION_CONFIDENCE': FACE_DETECTION_CONFIDENCE,
        'FACE_DETECTION_CONFIDENCE_HIGH': FACE_DETECTION_CONFIDENCE_HIGH,
        'FACE_RECOGNITION_THRESHOLD': FACE_RECOGNITION_THRESHOLD,
        'FACE_RECOGNITION_THRESHOLD_STRICT': FACE_RECOGNITION_THRESHOLD_STRICT,
        'FACE_RECOGNITION_THRESHOLD_RELAXED': FACE_RECOGNITION_THRESHOLD_RELAXED,
        'MIN_FACE_SIZE': MIN_FACE_SIZE,
        'MAX_FACE_SIZE': MAX_FACE_SIZE,
        'TEXTURE_VARIANCE_THRESHOLD': TEXTURE_VARIANCE_THRESHOLD,
        'BLINK_DETECTION_ENABLED': BLINK_DETECTION_ENABLED,
        'EYE_ASPECT_RATIO_THRESHOLD': EYE_ASPECT_RATIO_THRESHOLD
    }
    
    for key, value in configs.items():
        print(f"   {key}: {value}")
    
    return configs

def main():
    """Função principal de teste"""
    print("Iniciando testes das melhorias do sistema de reconhecimento facial...")
    print("=" * 60)
    
    try:
        # Testar configurações
        configs = test_configuration_values()
        print()
        
        # Testar detecção de qualidade
        faces_normal, faces_high = test_face_quality_detection()
        print()
        
        # Testar threshold adaptativo
        distance_adaptive, distance_fixed = test_adaptive_threshold()
        print()
        
        # Testar liveness
        liveness_stats = test_liveness_detection()
        print()
        
        # Resumo dos resultados
        print("RESUMO DOS TESTES:")
        print("=" * 60)
        print(f"Configurações carregadas: {len(configs)} parâmetros")
        print(f"Detecção de qualidade: Normal={faces_normal}, Alta={faces_high}")
        print(f"Threshold adaptativo: Distância adaptativa={distance_adaptive:.3f}, Fixa={distance_fixed:.3f}")
        print(f"Liveness: Movimento={liveness_stats['movement']:.3f}, Textura={liveness_stats['texture_variance']:.3f}")
        print(f"Piscadas detectadas: {liveness_stats['blink_count']}")
        
        print("\nTodos os testes concluídos com sucesso!")
        
    except Exception as e:
        print(f"Erro durante os testes: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
